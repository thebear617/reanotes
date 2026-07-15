(function () {
  'use strict';

  /* ===== DOM refs ===== */
  const navTree      = document.getElementById('navTree');
  const contentArea  = document.getElementById('contentArea');
  const welcome      = document.getElementById('welcome');
  const sidebar      = document.getElementById('sidebar');
  const menuToggle   = document.getElementById('menuToggle');
  const backdrop     = document.getElementById('sidebarBackdrop');
  const switcher     = document.getElementById('boardSwitcher');
  const topEyebrow   = document.getElementById('topEyebrow');
  const topTitle     = document.getElementById('topTitle');

  /* ===== State ===== */
  let currentBoard = null;   // board id
  let activeId     = null;

  /* ===== Helpers ===== */
  function boardData(id) { return BOARD_DATA[id]; }

  function updateTopBar(board) {
    topEyebrow.textContent = 'reanotes';
    topTitle.textContent = board ? board.name : '科研笔记';
    // 高亮当前板块
    if (switcher) {
      switcher.querySelectorAll('.switcher-item').forEach(el => {
        el.classList.toggle('active', board && el.dataset.board === board.id);
      });
    }
  }

  /* ===== 路由（hash 驱动） ===== */
  function parseHash() {
    const raw = (window.location.hash || '').replace(/^#/, '');
    if (!raw) return { board: null, page: null };
    const parts = raw.split('/');
    if (parts.length >= 2) return { board: parts[0], page: parts[1] };
    if (BOARD_DATA[parts[0]]) return { board: parts[0], page: null };
    return { board: currentBoard, page: parts[0] };
  }

  function route() {
    const { board, page } = parseHash();
    if (!board || !BOARD_DATA[board]) {
      // 无 hash 或无效板块 → 跳转到第一个板块
      window.location.hash = BOARDS[0].id;
      return;
    }
    if (currentBoard !== board) enterBoard(board);
    if (page && (BOARD_DATA[board].content[page] || _isTranslationPage(page))) {
      renderContentPage(page);
    } else {
      renderBoardHome(board);
    }
  }

  function _isTranslationPage(id) {
    var m = id && id.match(/^trans-(.+)$/);
    return m && window.PAPER_TRANSLATIONS && window.PAPER_TRANSLATIONS[m[1]];
  }

  /* ===== 总览仪表盘 ===== */
  function renderDashboard() {
    currentBoard = null;
    activeId = null;
    document.body.classList.add('on-dashboard');   // 隐藏侧边栏，内容居中
    closeSidebar();
    document.querySelectorAll('.nav-item a').forEach(el => el.classList.remove('active'));
    navTree.innerHTML = '';
    welcome.hidden = false;
    contentArea.hidden = true;
    updateTopBar(null);

    let html = `<div class="dash">
      <div class="dash-hero">
        <span class="dash-eyebrow">REANOTES</span>
        <h2 class="dash-title">科研笔记总站</h2>
        <p class="dash-desc">个人科研笔记的知识索引。从下方选择一个板块，或直接用顶栏切换器开始浏览。</p>
      </div>
      <div class="dash-grid">`;
    BOARDS.forEach(b => {
      html += `<a href="#${b.id}" class="dash-card" data-board="${b.id}" style="--accent:${b.accent}">
        <span class="dash-card-icon">${b.icon}</span>
        <span class="dash-card-name">${b.name}</span>
        <span class="dash-card-desc">${b.desc}</span>
        <span class="dash-card-go">进入浏览 →</span>
      </a>`;
    });
    html += `</div></div>`;
    welcome.innerHTML = html;

    welcome.querySelectorAll('.dash-card').forEach(card => {
      card.addEventListener('click', function (e) {
        e.preventDefault();
        window.location.hash = card.dataset.board;
      });
    });
  }

  /* ===== 进入某板块（仅搭好骨架，不渲染内容） ===== */
  function enterBoard(id) {
    const data = boardData(id);
    if (!data) return;
    currentBoard = id;
    document.body.classList.remove('on-dashboard');   // 进入板块：恢复侧边栏
    const board = BOARDS.find(b => b.id === id);
    renderNav(data.navTree);
    updateTopBar(board);
  }

  /* ===== 板块首页 ===== */
  function renderBoardHome(id) {
    const data = boardData(id);
    if (!data) return;
    if (currentBoard !== id) enterBoard(id);
    activeId = null;
    document.querySelectorAll('.nav-item a').forEach(el => el.classList.remove('active'));
    welcome.hidden = false;
    contentArea.hidden = true;

    const home = data.home || {};
    let html = '';
    html += `<div class="home-hero">
      <h2 class="home-hero-title">${home.title || ''}</h2>
      <p class="home-hero-desc">${home.desc || ''}</p>
    </div>`;

    if (home.gridCards && home.gridCards.length) {
      html += `<section class="home-section">
        <h3 class="home-section-title">快速入口</h3>
        <div class="home-grid">`;
      home.gridCards.forEach(card => {
        html += `<a href="#${id}/${card.id}" class="home-card" data-page="${card.id}">
          <span class="home-card-icon">${card.icon}</span>
          <span class="home-card-title">${card.title}</span>
          <span class="home-card-desc">${card.desc}</span>
        </a>`;
      });
      html += `</div></section>`;
    }

    if (home.quickRef && home.quickRef.length) {
      html += `<section class="home-section">
        <h3 class="home-section-title">速查</h3>
        <div class="quickref-grid">`;
      home.quickRef.forEach(item => {
        html += `<div class="quickref-card">
          <div class="quickref-label">${item.label}</div>
          <div class="quickref-slogan">${item.slogan}</div>
          <div class="quickref-models">${item.models}</div>
        </div>`;
      });
      html += `</div></section>`;
    }

    if (home.recentUpdates && home.recentUpdates.length) {
      html += `<section class="home-section">
        <h3 class="home-section-title">最近更新</h3>
        <div class="updates-list">`;
      home.recentUpdates.forEach(item => {
        html += `<a href="#${id}/${item.id}" class="updates-item" data-page="${item.id}">
          <span class="updates-date">${item.date}</span>
          <span class="updates-text">${item.text}</span>
          <span class="updates-arrow">→</span>
        </a>`;
      });
      html += `</div></section>`;
    }

    welcome.innerHTML = html;

    welcome.querySelectorAll('.home-card, .updates-item').forEach(el => {
      el.addEventListener('click', function (e) {
        e.preventDefault();
        window.location.hash = id + '/' + this.dataset.page;
      });
    });
  }

  /* ===== 侧边栏 ===== */
  function renderNav(navTreeData) {
    navTree.innerHTML = '';
    navTreeData.forEach(item => {
      if (item.type === 'divider') {
        const div = document.createElement('li');
        div.className = 'nav-divider';
        navTree.appendChild(div);
        return;
      }

      if (item.children) {
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
          a.addEventListener('click', function (e) {
            e.preventDefault();
            window.location.hash = currentBoard + '/' + child.id;
          });
          childLi.appendChild(a);
          ul.appendChild(childLi);
        });
        li.appendChild(ul);
        navTree.appendChild(li);

        toggle.addEventListener('click', function (e) {
          e.stopPropagation();
          const targetUl = document.getElementById('child-' + this.dataset.target);
          const isOpen = targetUl.classList.toggle('open');
          this.classList.toggle('open', isOpen);
        });
      } else {
        const li = document.createElement('li');
        li.className = 'nav-item';
        const a = document.createElement('a');
        a.href = '#';
        a.dataset.id = item.id;
        a.innerHTML = `
          <span class="nav-icon">${item.icon || ''}</span>
          <span class="nav-label">${item.label}</span>
        `;
        a.addEventListener('click', function (e) {
          e.preventDefault();
          window.location.hash = currentBoard + '/' + item.id;
        });
        li.appendChild(a);
        navTree.appendChild(li);
      }
    });
  }

  /* ===== 内容页 ===== */
  function renderContentPage(id) {
    const data = boardData(currentBoard);
    if (!data) return;
    var page = data.content[id];

    // 翻译路由：id 格式为 trans-<arxivId>（如 trans-1706.03762）
    if (!page) {
      var transMatch = id && id.match(/^trans-(.+)$/);
      if (transMatch && window.PAPER_TRANSLATIONS) {
        var transData = window.PAPER_TRANSLATIONS[transMatch[1]];
        if (transData) {
          page = {
            title: transData.title,
            desc: '翻译日期: ' + transData.date,
            article: transData.article,
          };
        }
      }
    }
    if (!page) return;

    // 侧栏高亮 + 展开父分类
    document.querySelectorAll('.nav-item a').forEach(el => el.classList.remove('active'));
    const link = document.querySelector(`.nav-item a[data-id="${id}"]`);
    if (link) {
      link.classList.add('active');
      const parentUl = link.closest('.nav-children');
      if (parentUl && !parentUl.classList.contains('open')) {
        parentUl.classList.add('open');
        const toggle = parentUl.closest('.nav-item')?.querySelector('.nav-toggle');
        if (toggle) toggle.classList.add('open');
      }
    }
    activeId = id;
    welcome.hidden = true;
    contentArea.hidden = false;

    let html = `<div class="page-section">`;
    html += `<div class="breadcrumb"><a href="#${currentBoard}" class="breadcrumb-home">🏠 首页</a> <span class="breadcrumb-sep">/</span> <span>${page.title.replace(/^[^\s]+\s/, '') || page.title}</span></div>`;
    html += `<h2 class="page-title">${page.title}</h2>`;
    if (page.desc) html += `<p class="page-desc">${page.desc}</p>`;

    if (page.cards) {
      html += '<div class="card-group">';
      page.cards.forEach((card, idx) => {
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

    if (page.article) {
      // 整页连续渲染（论文翻译等场景）：直接注入完整 HTML
      html += '<div class="article-body">' + page.article + '</div>';
    }

    html += '</div>';

    if (page.linkSections) {
      page.linkSections.forEach(function (section) {
        html += '<section class="link-section"><h3 class="link-section-title">' + section.title + '</h3><div class="link-grid">';
        section.items.forEach(function (item) {
          html += '<a class="venue-card" href="' + item.url + '" target="_blank" rel="noopener">'
                + '<span class="venue-head">'
                + '<span class="venue-name">' + item.name + '</span>'
                + '<span class="venue-field field-' + (item.kind || 'ml') + '">' + item.field + '</span>'
                + '<span class="venue-arrow">↗</span>'
                + '</span>'
                + '<span class="venue-desc">' + item.desc + '</span>'
                + (item.note ? '<span class="venue-note">' + item.note + '</span>' : '')
                + '</a>';
        });
        html += '</div></section>';
      });
    }

    if (page.litTable) {
      var t = page.litTable;
      html += '<div class="lit-table-wrap"><table class="lit-table"><thead><tr>';
      t.columns.forEach(function (col) {
        html += '<th>' + col.label + '</th>';
      });
      html += '</tr></thead><tbody>';
      t.rows.forEach(function (row) {
        html += '<tr>';
        t.columns.forEach(function (col) {
          var val = row[col.key];
          var cell = '';
          if (col.type === 'link') {
            // 检查是否有翻译
            var arxivMatch = row.url && row.url.match(/arxiv\.org\/abs\/([\d.]+(?:v\d+)?)/);
            var arxivId = arxivMatch ? arxivMatch[1] : '';
            var hasTranslation = arxivId && window.PAPER_TRANSLATIONS && window.PAPER_TRANSLATIONS[arxivId];
            if (hasTranslation) {
              cell = '<a class="lit-name lit-translated" href="#' + currentBoard + '/trans-' + arxivId + '">'
                   + val + ' <span class="lit-badge">📖 中文版</span></a>';
            } else {
              cell = '<a class="lit-name" href="' + row.url + '" target="_blank" rel="noopener">'
                   + val + ' <span class="lit-arrow">↗</span></a>';
            }
          } else if (col.type === 'tags') {
            cell = (val || []).map(function (tg) { return '<span class="lit-tag">' + tg + '</span>'; }).join('');
          } else if (col.type === 'domain') {
            cell = '<span class="lit-chip d-' + (row.dkind || 'general') + '">' + val + '</span>';
          } else if (col.type === 'status') {
            cell = '<span class="lit-chip s-' + (row.statusKind || 'unread') + '">' + val + '</span>';
          } else {
            cell = '<span class="lit-text">' + (val || '') + '</span>';
          }
          html += '<td>' + cell + '</td>';
        });
        html += '</tr>';
      });
      html += '</tbody></table></div>';
    }

    html += '</div>';
    contentArea.innerHTML = html;

    // KaTeX 渲染（论文翻译板块用）
    if (window.renderMathInElement) {
      try {
        renderMathInElement(contentArea, {
          delimiters: [
            { left: '$$', right: '$$', display: true },
            { left: '$', right: '$', display: false },
            { left: '\\[', right: '\\]', display: true },
            { left: '\\(', right: '\\)', display: false },
          ],
          throwOnError: false,
        });
      } catch (e) {
        console.warn('KaTeX render failed:', e);
      }
    }

    // 卡片折叠
    document.querySelectorAll('.card-header').forEach(header => {
      header.addEventListener('click', function () {
        const card = document.getElementById(this.dataset.card);
        if (!card) return;
        const body = card.querySelector('.card-body');
        const isCollapsed = card.classList.contains('collapsed');
        if (isCollapsed) {
          card.classList.remove('collapsed');
          card.classList.add('open');
          const inner = body.querySelector('.card-inner');
          body.style.maxHeight = (inner ? inner.scrollHeight + 40 : 2000) + 'px';
        } else {
          card.classList.add('collapsed');
          card.classList.remove('open');
          body.style.maxHeight = '0';
        }
      });
    });

    // 面包屑首页 → 板块首页
    const homeLink = contentArea.querySelector('.breadcrumb-home');
    if (homeLink) {
      homeLink.addEventListener('click', function (e) {
        e.preventDefault();
        window.location.hash = currentBoard;
      });
    }

    closeSidebar();
  }

  /* ===== 板块切换器 ===== */
  function renderBoardSwitcher() {
    if (!switcher) return;
    switcher.innerHTML = '';

    BOARDS.forEach(b => {
      const a = document.createElement('a');
      a.href = '#' + b.id;
      a.className = 'switcher-item';
      a.dataset.board = b.id;
      a.style.setProperty('--accent', b.accent);
      a.innerHTML = `<span class="switcher-icon">${b.icon}</span><span>${b.name}</span>`;
      switcher.appendChild(a);
    });

    switcher.querySelectorAll('.switcher-item').forEach(el => {
      el.addEventListener('click', function (e) {
        e.preventDefault();
        window.location.hash = this.dataset.board;
      });
    });
  }

  /* ===== Sidebar open/close ===== */
  function openSidebar() { sidebar.classList.add('open'); backdrop.hidden = false; }
  function closeSidebar() { sidebar.classList.remove('open'); backdrop.hidden = true; }

  menuToggle.addEventListener('click', function () {
    if (sidebar.classList.contains('open')) closeSidebar(); else openSidebar();
  });
  backdrop.addEventListener('click', closeSidebar);
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeSidebar();
  });

  /* ===== 顶栏点击：eyebrow→第一个板块，title→板块首页 ===== */
  document.querySelector('.top-bar-left').addEventListener('click', function (e) {
    const target = e.target.closest('.top-title, .top-eyebrow');
    if (!target) return;
    e.preventDefault();
    if (target.classList.contains('top-eyebrow')) {
      window.location.hash = BOARDS[0].id;
    } else if (currentBoard) {
      window.location.hash = currentBoard;
    } else {
      window.location.hash = BOARDS[0].id;
    }
  });

  /* ===== Init ===== */
  renderBoardSwitcher();
  window.addEventListener('hashchange', route);
  route();
})();
