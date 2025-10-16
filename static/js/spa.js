class SPA {
    constructor() {
        this.currentProject = null;
        this.sidebarState = null;
        this.prefetchCache = new Map();
        this.init();
    }

    init() {
        this.setupInterceptors();
        this.handlePopState();
        this.detectCurrentProject();
        this.setupKeyboardNavigation();
        this.setupPrefetch();
    }

    detectCurrentProject() {
        // detect projet md actuel via url
        const match = window.location.pathname.match(/^\/md\/([^\/]+)/);
        if (match) {
            this.currentProject = match[1];
            this.saveSidebarState();
        }
    }

    saveSidebarState() {
        const sidebar = document.querySelector('.md-sidebar');
        if (!sidebar) return;

        const openFolders = [];
        sidebar.querySelectorAll('details.folder').forEach((details, index) => {
            if (details.open) {
                openFolders.push(index);
            }
        });

        this.sidebarState = {
            openFolders: openFolders,
            scrollTop: sidebar.scrollTop
        };
    }

    restoreSidebarState() {
        if (!this.sidebarState) return;

        const sidebar = document.querySelector('.md-sidebar');
        if (!sidebar) return;

        sidebar.querySelectorAll('details.folder').forEach((details, index) => {
            if (this.sidebarState.openFolders.includes(index)) {
                details.open = true;
                const icon = details.querySelector('.folder-icon');
                if (icon) icon.textContent = '📂';
            }
        });

        sidebar.scrollTop = this.sidebarState.scrollTop;
    }

    setupInterceptors() {
        // delegation pour capturer tous liens data-spa
        document.body.addEventListener('click', (e) => {
            const link = e.target.closest('a[data-spa]');
            if (link && !link.hasAttribute('target')) {
                e.preventDefault();
                const url = link.getAttribute('href');
                this.navigate(url);
            }
        });
    }

    handlePopState() {
        window.addEventListener('popstate', () => {
            this.loadPage(window.location.pathname, false);
        });
    }

    navigate(url) {
        if (window.location.pathname === url) return;
        this.loadPage(url, true);
    }

    async loadPage(url, pushState = true) {
        const container = document.querySelector('.main-content');
        if (!container) return;

        // detect si on reste dans même projet md
        const oldProject = this.currentProject;
        const newProject = url.match(/^\/md\/([^\/]+)/)?.[1];
        const sameProject = oldProject && newProject && oldProject === newProject;

        // save sidebar state si dans même projet
        if (sameProject) {
            this.saveSidebarState();
        }

        // anim fade out
        const content = container.querySelector('.md-content');
        const targetElement = sameProject && content ? content : container;
        
        targetElement.classList.add('fade-out-spa');
        await new Promise(resolve => setTimeout(resolve, 200));

        try {
            const response = await fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                redirect: 'follow'
            });

            if (!response.ok) {
                throw new Error(`http error ${response.status}`);
            }

            const contentType = response.headers.get('content-type') || '';
            if (!contentType.includes('text/html')) {
                window.location.href = url;
                return;
            }

            const html = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');

            this.updateContentFromDocument(doc, sameProject);

            const finalUrl = new URL(response.url, window.location.origin);
            if (pushState) {
                const relativeUrl = `${finalUrl.pathname}${finalUrl.search}${finalUrl.hash}`;
                window.history.pushState({}, '', relativeUrl);
            }

            const newTitle = doc.querySelector('title');
            if (newTitle) {
                document.title = newTitle.textContent;
            }

            // update current project
            this.currentProject = newProject;

            window.scrollTo({ top: 0, behavior: 'smooth' });

            // anim fade in
            targetElement.classList.remove('fade-out-spa');
            targetElement.classList.add('fade-in-spa');
            setTimeout(() => targetElement.classList.remove('fade-in-spa'), 300);

        } catch (error) {
            console.error('spa nav error:', error);
            window.location.href = url;
        }
    }

    updateContentFromDocument(doc, sameProject) {
        const newContent = doc.querySelector('.main-content');
        const container = document.querySelector('.main-content');

        if (!newContent || !container) return;

        if (sameProject) {
            // update uniquement contenu md et breadcrumb
            const newMdContent = newContent.querySelector('.md-content');
            const currentMdContent = container.querySelector('.md-content');
            const newBreadcrumb = newContent.querySelector('.breadcrumb');
            const currentBreadcrumb = container.querySelector('.breadcrumb');

            if (newMdContent && currentMdContent) {
                currentMdContent.innerHTML = newMdContent.innerHTML;
            }

            if (newBreadcrumb && currentBreadcrumb) {
                currentBreadcrumb.innerHTML = newBreadcrumb.innerHTML;
            }

            // update active file dans sidebar
            const sidebar = container.querySelector('.md-sidebar');
            if (sidebar) {
                sidebar.querySelectorAll('.file-item').forEach(item => {
                    item.classList.remove('active');
                    const icon = item.querySelector('.file-icon');
                    if (icon && icon.textContent === '▶') {
                        icon.textContent = '📝';
                    }
                });

                const newSidebar = newContent.querySelector('.md-sidebar');
                if (newSidebar) {
                    const activeFile = newSidebar.querySelector('.file-item.active');
                    if (activeFile) {
                        const activeLink = activeFile.querySelector('.file-link');
                        const currentLink = sidebar.querySelector(`[href="${activeLink.getAttribute('href')}"]`);
                        if (currentLink) {
                            const currentItem = currentLink.closest('.file-item');
                            if (currentItem) {
                                currentItem.classList.add('active');
                                const icon = currentItem.querySelector('.file-icon');
                                if (icon) icon.textContent = '▶';
                            }
                        }
                    }
                }

                // restore sidebar state
                this.restoreSidebarState();
            }
        } else {
            // full replace pour changement projet
            container.innerHTML = newContent.innerHTML;
            this.initializeFolders();
        }
    }

    initializeFolders() {
        // initialiser icônes dossiers et event listeners
        document.querySelectorAll('.folder-summary').forEach(summary => {
            const details = summary.parentElement;
            const icon = summary.querySelector('.folder-icon');
            
            // set icône initiale
            if (icon) {
                icon.textContent = details.open ? '📂' : '📁';
            }

            // ajouter listener avec animation
            summary.addEventListener('click', (e) => {
                if (details.open) {
                    // fermeture: empêcher et animer
                    e.preventDefault();
                    
                    const content = details.querySelector('.folder-content');
                    if (content) {
                        // anim items qui remontent
                        const items = content.querySelectorAll(':scope > *');
                        items.forEach((item, index) => {
                            item.style.animation = `itemSlideUp 0.2s cubic-bezier(0.36, 0, 0.66, -0.56) forwards`;
                            item.style.animationDelay = `${index * 0.02}s`;
                        });
                        
                        // anim folder qui remonte
                        content.style.animation = 'folderSlideUp 0.25s cubic-bezier(0.36, 0, 0.66, -0.56) forwards';
                    }
                    
                    // fermer après anim
                    setTimeout(() => {
                        details.open = false;
                        if (icon) icon.textContent = '📁';
                        // reset anims pour prochaine ouverture
                        if (content) {
                            content.style.animation = '';
                            const items = content.querySelectorAll(':scope > *');
                            items.forEach(item => {
                                item.style.animation = '';
                                item.style.animationDelay = '';
                            });
                        }
                    }, 250);
                } else {
                    // ouverture: laisser faire et update icône
                    setTimeout(() => {
                        if (icon) icon.textContent = '📂';
                    }, 10);
                }
            });
        });

        // setup search
        this.setupSearch();
        
        // setup collapse/expand buttons
        this.setupFolderControls();
    }

    setupSearch() {
        const searchInput = document.getElementById('file-search');
        if (!searchInput) return;

        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase().trim();
            const fileItems = document.querySelectorAll('.file-item');
            const folders = document.querySelectorAll('.folder');

            if (!query) {
                // reset all
                fileItems.forEach(item => item.style.display = '');
                folders.forEach(folder => folder.style.display = '');
                return;
            }

            // filter files
            fileItems.forEach(item => {
                const fileName = item.querySelector('.file-name')?.textContent.toLowerCase() || '';
                if (fileName.includes(query)) {
                    item.style.display = '';
                    item.classList.add('search-highlight');
                } else {
                    item.style.display = 'none';
                    item.classList.remove('search-highlight');
                }
            });

            // show/hide folders based on visible children
            folders.forEach(folder => {
                const hasVisibleChildren = Array.from(folder.querySelectorAll('.file-item'))
                    .some(item => item.style.display !== 'none');
                
                if (hasVisibleChildren) {
                    folder.style.display = '';
                    folder.open = true; // auto-expand
                    const icon = folder.querySelector('.folder-icon');
                    if (icon) icon.textContent = '📂';
                } else {
                    folder.style.display = 'none';
                }
            });
        });
    }

    setupFolderControls() {
        const expandBtn = document.getElementById('expand-all');
        const collapseBtn = document.getElementById('collapse-all');

        if (expandBtn) {
            expandBtn.addEventListener('click', () => {
                document.querySelectorAll('.folder').forEach((folder, folderIndex) => {
                    if (!folder.open) {
                        setTimeout(() => {
                            folder.open = true;
                            const icon = folder.querySelector('.folder-icon');
                            if (icon) icon.textContent = '📂';
                        }, folderIndex * 50);
                    }
                });
            });
        }

        if (collapseBtn) {
            collapseBtn.addEventListener('click', () => {
                const openFolders = Array.from(document.querySelectorAll('.folder[open]'));
                
                openFolders.forEach((folder, folderIndex) => {
                    const content = folder.querySelector('.folder-content');
                    
                    setTimeout(() => {
                        if (content) {
                            // anim items qui remontent
                            const items = content.querySelectorAll(':scope > *');
                            items.forEach((item, itemIndex) => {
                                item.style.animation = `itemSlideUp 0.2s cubic-bezier(0.36, 0, 0.66, -0.56) forwards`;
                                item.style.animationDelay = `${itemIndex * 0.02}s`;
                            });
                            
                            // anim folder
                            content.style.animation = 'folderSlideUp 0.25s cubic-bezier(0.36, 0, 0.66, -0.56) forwards';
                        }
                        
                        // fermer après anim
                        setTimeout(() => {
                            folder.open = false;
                            const icon = folder.querySelector('.folder-icon');
                            if (icon) icon.textContent = '📁';
                            
                            // reset anims
                            if (content) {
                                content.style.animation = '';
                                const items = content.querySelectorAll(':scope > *');
                                items.forEach(item => {
                                    item.style.animation = '';
                                    item.style.animationDelay = '';
                                });
                            }
                        }, 250);
                    }, folderIndex * 50);
                });
            });
        }
    }

    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            // uniquement dans pages markdown
            if (!document.querySelector('.md-sidebar')) return;
            
            // éviter conflit avec inputs
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

            const fileItems = Array.from(document.querySelectorAll('.file-item'));
            const activeItem = fileItems.find(item => item.classList.contains('active'));
            if (!activeItem) return;

            const currentIndex = fileItems.indexOf(activeItem);
            let targetIndex = -1;

            if (e.key === 'ArrowDown') {
                e.preventDefault();
                targetIndex = Math.min(currentIndex + 1, fileItems.length - 1);
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                targetIndex = Math.max(currentIndex - 1, 0);
            }

            if (targetIndex >= 0 && targetIndex !== currentIndex) {
                const targetLink = fileItems[targetIndex].querySelector('.file-link');
                if (targetLink) {
                    targetLink.click();
                    // scroll sidebar to target
                    setTimeout(() => {
                        fileItems[targetIndex].scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    }, 100);
                }
            }
        });
    }

    setupPrefetch() {
        document.body.addEventListener('mouseenter', (e) => {
            const link = e.target.closest('a[data-spa]');
            if (link && link.href && !this.prefetchCache.has(link.href)) {
                this.prefetchPage(link.href);
            }
        }, true);
    }

    async prefetchPage(url) {
        // éviter prefetch si déjà en cache
        if (this.prefetchCache.has(url)) return;

        try {
            const response = await fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (response.ok) {
                const html = await response.text();
                this.prefetchCache.set(url, html);
                
                // limit cache size
                if (this.prefetchCache.size > 10) {
                    const firstKey = this.prefetchCache.keys().next().value;
                    this.prefetchCache.delete(firstKey);
                }
            }
        } catch (error) {
            // silent fail pour prefetch
        }
    }

    async loadPage(url, pushState = true) {
        const container = document.querySelector('.main-content');
        if (!container) return;

        // detect si on reste dans même projet md
        const oldProject = this.currentProject;
        const newProject = url.match(/^\/md\/([^\/]+)/)?.[1];
        const sameProject = oldProject && newProject && oldProject === newProject;

        // save sidebar state si dans même projet
        if (sameProject) {
            this.saveSidebarState();
        }

        // anim fade out
        const content = container.querySelector('.md-content');
        const targetElement = sameProject && content ? content : container;
        
        targetElement.classList.add('fade-out-spa');
        await new Promise(resolve => setTimeout(resolve, 200));

        try {
            let html;
            // check cache
            if (this.prefetchCache.has(url)) {
                html = this.prefetchCache.get(url);
                this.prefetchCache.delete(url);
            } else {
                const response = await fetch(url, {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    redirect: 'follow'
                });

                if (!response.ok) {
                    throw new Error(`http error ${response.status}`);
                }

                const contentType = response.headers.get('content-type') || '';
                if (!contentType.includes('text/html')) {
                    window.location.href = url;
                    return;
                }

                html = await response.text();
            }

            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');

            this.updateContentFromDocument(doc, sameProject);

            const finalUrl = new URL(url, window.location.origin);
            if (pushState) {
                const relativeUrl = `${finalUrl.pathname}${finalUrl.search}${finalUrl.hash}`;
                window.history.pushState({}, '', relativeUrl);
            }

            const newTitle = doc.querySelector('title');
            if (newTitle) {
                document.title = newTitle.textContent;
            }

            // update current project
            this.currentProject = newProject;

            window.scrollTo({ top: 0, behavior: 'smooth' });

            // anim fade in
            targetElement.classList.remove('fade-out-spa');
            targetElement.classList.add('fade-in-spa');
            setTimeout(() => targetElement.classList.remove('fade-in-spa'), 300);

        } catch (error) {
            console.error('spa nav error:', error);
            window.location.href = url;
        }
    }
}

// initialisation
document.addEventListener('DOMContentLoaded', () => {
    if (document.body.classList.contains('spa-enabled')) {
        window.spaInstance = new SPA();
        window.spaInstance.initializeFolders();
    }
});