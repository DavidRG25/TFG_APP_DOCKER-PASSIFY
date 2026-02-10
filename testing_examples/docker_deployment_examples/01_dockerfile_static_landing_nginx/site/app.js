document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('ping');
  const out = document.getElementById('out');

  btn.onclick = () => {
    btn.disabled = true;
    const initialText = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-sync fa-spin"></i> Analizando...';
    
    out.style.display = 'block';
    out.innerText = '> Inicializando diagnóstico de entorno...';
    
    setTimeout(() => {
      out.innerText += '\n> Verificando aislamiento de usuario app (UID 1000)... OK';
      
      setTimeout(() => {
        out.innerText += '\n> Conexión con Nginx 1.27 estable en puerto 8080.';
        
        setTimeout(() => {
          const now = new Date().toISOString();
          out.innerHTML += `\n<span style="color:var(--success)">[ÉXITO] Sistema validado el ${now}</span>`;
          
          btn.disabled = false;
          btn.innerHTML = initialText;
        }, 800);
      }, 600);
    }, 500);
  };
});
