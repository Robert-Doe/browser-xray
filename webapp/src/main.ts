import './style.css';
import { renderModuleLibrary, wireModuleLibrary } from './library/render';

const app = document.getElementById('app')!;

app.innerHTML = `
  <div class="topbar">
    <div class="topbar-left">
      <div class="brand">Browser X-Ray</div>
      <div class="brand-sub">35 modules, 2 tracks &middot; the OS floor a browser stands on, then the engine built on top of it</div>
    </div>
    <div class="links">
      <a href="https://github.com/Robert-Doe/browser-xray" target="_blank" rel="noopener">GitHub</a>
      <a href="https://robertdoe.com">&larr; robertdoe.com</a>
    </div>
  </div>
  <div class="app-main" id="module-library"></div>
`;

renderModuleLibrary(document.getElementById('module-library')!);
wireModuleLibrary();
