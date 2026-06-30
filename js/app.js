(function () {
  'use strict';

  /* ===== DOM refs ===== */
  const navTree       = document.getElementById('navTree');
  const contentArea   = document.getElementById('contentArea');
  const welcome       = document.getElementById('welcome');
  const sidebar       = document.getElementById('sidebar');
  const menuToggle    = document.getElementById('menuToggle');
  const backdrop      = document.getElementById('sidebarBackdrop');

  /* ===== State ===== */
  let activeId = null;      // currently active nav item id

  /* ===== Render sidebar ===== */
  function renderNav() {
    NAV_TREE.forEach(item => {
      if (item.type === 'divider') {
        const div = document.createElement('li');
        div.className = 'nav-divider';
        navTree.appendChild(div);
        return;
      }

      if (item.children) {
        // Category node with children
        const li = document.createElement('li');
        li.className = 'nav-item';
        const toggle = document.createElement('button');
        toggle.className = 'nav-toggle';
        toggle.dataset.target = item.id;
        toggle.innerHTML = `
          <span class="nav-icon">${item.icon || ''}</span>
          <span class="nav-label">${item.label}</span>
          <span class="nav-arrow">▶</span>
        `;
        li.appendChild(toggle);

        const ul = document.createElement('ul');
        ul.className = 'nav-children';
        ul.id = 'child-' + item.id;
        item.children.forEach(child => {
          const childLi = document.createElement('li');
          childLi.className = 'nav-item';
          const a = document.createElement('a');
          a.href = '#';
          a.dataset.id = child.id;
          a.textContent = child.label;
          childLi.appendChild(a);
          ul.appendChild(childLi);
        });
        li.appendChild(ul);
        navTree.appendChild(li);

        // Toggle expand
        toggle.addEventListener('click', function (e) {
          e.stopPropagation();
          const targetUl = document.getElementById('child-' + this.dataset.target);
          const isOpen = targetUl.classList.toggle('open');
          this.classList.toggle('open', isOpen);
        });

      } else {
        // Leaf node
        const li = document.createElement('li');
        li.className = 'nav-item';
        const a = document.createElement('a');
        a.href = '#';
        a.dataset.id = item.id;
        a.innerHTML = `
          <span class="nav-icon">${item.icon || ''}</span>
          <span class="nav-label">${item.label}</span>
        `;
        li.appendChild(a);
        navTree.appendChild(li);
      }
    });
  }

  /* ===== Click handler: nav link ===== */
  function handleNavClick(e) {
    const a = e.target.closest('a[data-id]');
    if (!a) return;
    e.preventDefault();

    const id = a.dataset.id;
    if (id === activeId) return;

    // Update active state
    document.querySelectorAll('.nav-item a').forEach(el => el.classList.remove('active'));
    a.classList.add('active');

    // Open parent category if collapsed
    const parentUl = a.closest('.nav-children');
    if (parentUl && !parentUl.classList.contains('open')) {
      parentUl.classList.add('open');
      const toggle = parentUl.closest('.nav-item')?.querySelector('.nav-toggle');
      if (toggle) toggle.classList.add('open');
    }

    activeId = id;
    renderContent(id);

    // Close sidebar on mobile
    closeSidebar();
  }

  /* ===== Render content ===== */
  function renderContent(id) {
    const data = CONTENT[id];
    if (!data) return;

    welcome.hidden = true;
    contentArea.hidden = false;

    let html = `<div class="page-section"><h2 class="page-title">${data.title}</h2>`;
    if (data.desc) {
      html += `<p class="page-desc">${data.desc}</p>`;
    }

    if (data.cards) {
      html += '<div class="card-group">';
      data.cards.forEach((card, idx) => {
        const cardId = 'card-' + id + '-' + idx;
        const collapsed = card.expanded ? '' : 'collapsed';
        html += `
          <div class="card ${collapsed}" id="${cardId}">
            <div class="card-header" data-card="${cardId}">
              <span class="card-icon">${card.icon}</span>
              <span class="card-title">${card.title}</span>
              ${card.tags ? card.tags.map(t => `<span class="tag-pill tag-accent">${t}</span>`).join('') : ''}
              <span class="card-arrow">▶</span>
            </div>
            <div class="card-body" style="max-height: ${card.expanded ? '2000px' : '0'}">
              <div class="card-inner">${card.body}</div>
            </div>
          </div>`;
      });
      html += '</div>';
    }

    html += '</div>';
    contentArea.innerHTML = html;

    // Re-bind card toggle events
    document.querySelectorAll('.card-header').forEach(header => {
      header.addEventListener('click', function () {
        const card = document.getElementById(this.dataset.card);
        if (!card) return;
        const body = card.querySelector('.card-body');
        const isCollapsed = card.classList.contains('collapsed');

        if (isCollapsed) {
          card.classList.remove('collapsed');
          card.classList.add('open');
          // Set max-height for animation
          const inner = body.querySelector('.card-inner');
          body.style.maxHeight = (inner ? inner.scrollHeight + 40 : 2000) + 'px';
        } else {
          card.classList.add('collapsed');
          card.classList.remove('open');
          body.style.maxHeight = '0';
        }
      });
    });
  }

  /* ===== Sidebar open/close ===== */
  function openSidebar() {
    sidebar.classList.add('open');
    backdrop.hidden = false;
  }

  function closeSidebar() {
    sidebar.classList.remove('open');
    backdrop.hidden = true;
  }

  menuToggle.addEventListener('click', function () {
    if (sidebar.classList.contains('open')) {
      closeSidebar();
    } else {
      openSidebar();
    }
  });

  backdrop.addEventListener('click', closeSidebar);

  /* ===== Keyboard escape ===== */
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeSidebar();
  });

  /* ===== Init ===== */
  renderNav();

  // Global nav click delegation
  navTree.addEventListener('click', handleNavClick);

  // If URL has hash, navigate to it
  if (window.location.hash) {
    const id = window.location.hash.slice(1);
    const targetLink = document.querySelector(`.nav-item a[data-id="${id}"]`);
    if (targetLink) {
      targetLink.click();
    }
  }

})();
