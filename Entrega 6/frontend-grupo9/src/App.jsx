import { useState, useEffect, useRef } from 'react';
import './App.css';

const GATEWAY_URL = "https://gateway-grupo9.inf326.nursoft.dev";

function App() {
  const [view, setView] = useState("LOGIN");
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState("CHATBOT"); 
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [publicChannels, setPublicChannels] = useState([]);
  const [myChannels, setMyChannels] = useState([]);
  const [selectedChannel, setSelectedChannel] = useState(null);
  
  const [newChannelName, setNewChannelName] = useState("");
  const [editChannelName, setEditChannelName] = useState("");
  const [messages, setMessages] = useState([{ author: "Bot", content: "Bienvenido al Sistema." }]);
  const [inputText, setInputText] = useState("");
  const messagesEndRef = useRef(null);

  const handleAuth = async (e, type) => {
    e.preventDefault();
    setLoading(true); setError("");
    const formUser = e.target.username?.value;
    const formEmail = e.target.email?.value;
    const formPass = e.target.password.value;

    const payload = {
        username_or_email: formUser || formEmail,
        email: formEmail,
        username: formUser,
        password: formPass
    };

    try {
      const endpoint = type === 'login' ? '/proxy/auth/login' : '/proxy/auth/register';
      const res = await fetch(`${GATEWAY_URL}${endpoint}`, {
        method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)
      });
      
      if (!res.ok) throw new Error("Error de autenticación / Servicio no disponible");
      
      if (type === 'login') {
        const safeUser = { username: payload.username_or_email || "Usuario" };
        setUser(safeUser);
        
        loadPublicChannels();
        loadMyChannels(safeUser.username);
        
        setView("DASHBOARD");
      } else {
        alert("Registro exitoso. Inicia sesión."); setView("LOGIN");
      }
    } catch (err) { setError(err.message); } finally { setLoading(false); }
  };

  const loadPublicChannels = async () => {
    try {
      const res = await fetch(`${GATEWAY_URL}/proxy/channels`);
      const data = await res.json();
      setPublicChannels(Array.isArray(data) ? data : []);
    } catch (e) { console.error(e); setPublicChannels([]); }
  };

  const loadMyChannels = async (username) => {
    if(!username) return;
    try {
      const res = await fetch(`${GATEWAY_URL}/proxy/channels/owner/${username}`);
      const data = await res.json();
      setMyChannels(Array.isArray(data) ? data : []);
    } catch (e) { console.error(e); setMyChannels([]); }
  };

  const handleCreateChannel = async (e) => {
    e.preventDefault();
    if (!newChannelName.trim()) return;
    try {
      const res = await fetch(`${GATEWAY_URL}/proxy/channels`, {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ name: newChannelName, owner_id: user?.username })
      });
      if (res.ok) {
        setNewChannelName("");
        setTimeout(() => loadMyChannels(user?.username), 500);
        setTimeout(loadPublicChannels, 500);
      } else alert("Error al crear");
    } catch (e) { alert("Error conexión"); }
  };

  const selectChannel = async (channel) => {
    if(!channel) return;
    setSelectedChannel(channel);
    setEditChannelName(channel.name || "");
    setActiveTab("CHANNEL_DETAILS");
    
    try {
        const id = channel._id || channel.id;
        if(id) {
            const res = await fetch(`${GATEWAY_URL}/proxy/channels/${id}`);
            if(res.ok) {
                const details = await res.json();
                if (details) setSelectedChannel(details);
            }
        }
    } catch(e) {}
  };

  const handleUpdateChannel = async () => {
    if (!selectedChannel) return;
    try {
      const id = selectedChannel._id || selectedChannel.id;
      await fetch(`${GATEWAY_URL}/proxy/channels/${id}`, {
        method: 'PUT', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ name: editChannelName, status: "active" })
      });
      alert("Actualizado");
      loadMyChannels(user?.username);
      loadPublicChannels();
    } catch(e) { alert("Error update"); }
  };

  const handleDeleteChannel = async () => {
    if (!selectedChannel) return;
    const id = selectedChannel._id || selectedChannel.id;
    await fetch(`${GATEWAY_URL}/proxy/channels/${id}`, { method: 'DELETE' });
    setActiveTab("CHATBOT");
    setSelectedChannel(null);
    setTimeout(() => {
        loadMyChannels(user?.username);
        loadPublicChannels();
    }, 500);
  };

  const handleReactivateChannel = async () => {
    if (!selectedChannel) return;
    const id = selectedChannel._id || selectedChannel.id;
    await fetch(`${GATEWAY_URL}/proxy/channels/${id}/reactivate`, { method: 'POST' });
    alert("Reactivado");
  };

  const sendMessage = async () => {
    if(!inputText) return;
    const text = inputText; setInputText("");
    setMessages(prev => [...prev, { author: "Yo", content: text, isMe: true }]);
    try {
      const res = await fetch(`${GATEWAY_URL}/api/chat`, {
        method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ text })
      });
      const data = await res.json();
      setMessages(prev => [...prev, { author: data.author, content: data.content, isMe: false }]);
    } catch (e) { setMessages(prev => [...prev, { author: "Sys", content: "Error bot" }]); }
  };
  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  if (view !== "DASHBOARD" || !user) {
    return (
      <div className="auth-container">
        <div className="auth-box">
          <div className="logo">🏛️</div>
          <h1>Campus G9</h1>
          <form onSubmit={(e) => handleAuth(e, view === "LOGIN" ? 'login' : 'register')}>
            {view === "REGISTER" && <input className="auth-input" name="email" type="email" placeholder="Email" required />}
            <input className="auth-input" name="username" placeholder="Usuario" required />
            <input className="auth-input" name="password" type="password" placeholder="Contraseña" required />
            <button className="auth-btn" type="submit" disabled={loading}>{loading ? "..." : (view==="LOGIN"?"Entrar":"Registrar")}</button>
          </form>
          <p onClick={() => setView(view==="LOGIN"?"REGISTER":"LOGIN")} className="auth-link">
            {view==="LOGIN"?"¿Crear cuenta?":"¿Iniciar Sesión?"}
          </p>
          {error && <div className="auth-error">{error}</div>}
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <aside className="sidebar">
        <div className="sidebar-header">
          <h3>Panel G9</h3>
          <button onClick={() => {loadPublicChannels(); loadMyChannels(user?.username)}} className="mini-refresh">↻</button>
        </div>
        
        <div className="sidebar-section">
          <h4>MIS CANALES</h4>
          <div className="channels-list">
            {myChannels.map((c, i) => (
              <div key={i} className={`channel-item ${selectedChannel?.id === c.id ? 'active' : ''}`} onClick={() => selectChannel(c)}>
                📢 {c.name}
              </div>
            ))}
          </div>
        </div>

        <div className="sidebar-section">
          <h4>PÚBLICOS</h4>
          <div className="channels-list">
            {publicChannels.map((c, i) => (
              <div key={i} className="channel-item" onClick={() => selectChannel(c)}>
                # {c.name}
              </div>
            ))}
          </div>
        </div>

        <div className="create-box">
            <form onSubmit={handleCreateChannel}>
                <input value={newChannelName} onChange={e => setNewChannelName(e.target.value)} placeholder="+ Nuevo" />
            </form>
        </div>

        <div className="user-profile-bar">
            <div className="avatar">
                {user.username ? user.username.charAt(0).toUpperCase() : "U"}
            </div>
            <div className="user-info">
                <div className="name">{user.username}</div>
                <div className="link" onClick={() => setActiveTab("CHATBOT")}>Ir al Chat</div>
            </div>
            <button className="logout-btn" onClick={() => setView("LOGIN")}>Salir</button>
        </div>
      </aside>

      <main className="main-content">
        {activeTab === "CHATBOT" ? (
          <div className="chat-wrapper">
            <div className="chat-header"><h2>🤖 Asistente Virtual</h2></div>
            <div className="chat-messages">
              {messages.map((m, i) => (
                <div key={i} className={`msg-row ${m.isMe ? 'me' : 'bot'}`}>
                    <div className="msg-bubble">
                        {!m.isMe && <small>{m.author}</small>}
                        {m.content}
                    </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
            <div className="chat-input-area">
              <input value={inputText} onChange={e => setInputText(e.target.value)} onKeyDown={e => e.key === 'Enter' && sendMessage()} placeholder="Escribe..." />
              <button onClick={sendMessage}>Enviar</button>
            </div>
          </div>
        ) : (
          <div className="details-wrapper">
            <div className="details-header">
                <h2>Configuración</h2>
                <button onClick={() => setActiveTab("CHATBOT")}>✕</button>
            </div>
            <div className="details-content">
                <div className="info-card">
                    <h3>Detalles</h3>
                    <p><strong>ID:</strong> {selectedChannel?._id || selectedChannel?.id}</p>
                    <p><strong>Dueño:</strong> {selectedChannel?.owner_id}</p>
                </div>
                <div className="info-card">
                    <h3>Editar</h3>
                    <div className="row">
                        <input value={editChannelName} onChange={e => setEditChannelName(e.target.value)} />
                        <button className="btn-primary" onClick={handleUpdateChannel}>Guardar</button>
                    </div>
                </div>
                <div className="info-card danger">
                    <h3>Acciones</h3>
                    <div className="row">
                        <button className="btn-warning" onClick={handleReactivateChannel}>Reactivar</button>
                        <button className="btn-danger" onClick={handleDeleteChannel}>Eliminar</button>
                    </div>
                </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;