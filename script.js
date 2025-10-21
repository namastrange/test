let contentItems = [];
let focusedItem = null;
let clickedItem = null;
let animationRunning = false;

function getRandomPosition() {
    const maxX = window.innerWidth - 320;
    const maxY = window.innerHeight - 300;

    return {
        x: Math.random() * Math.max(0, maxX),
        y: Math.random() * Math.max(0, maxY)
    };
}

function centerItem(item) {
    const centerX = (window.innerWidth / 2) - (item.offsetWidth / 2);
    const centerY = (window.innerHeight / 2) - (item.offsetHeight / 2);

    item.style.left = centerX + 'px';
    item.style.top = centerY + 'px';
}

function createContentItem(type, content) {
    const container = document.getElementById('content-container');
    const item = document.createElement('div');
    item.className = 'content-item ' + type + '-item';

    const pos = getRandomPosition();
    item.setAttribute('data-base-x', pos.x);
    item.setAttribute('data-base-y', pos.y);
    item.setAttribute('data-velocity-x', (Math.random() - 0.5) * 0.3);
    item.setAttribute('data-velocity-y', (Math.random() - 0.5) * 0.3);
    item.setAttribute('data-wiggle-phase', Math.random() * Math.PI * 2);

    item.style.left = pos.x + 'px';
    item.style.top = pos.y + 'px';

    if (type === 'text') {
        const textContent = document.createElement('p');
        textContent.textContent = content;
        item.appendChild(textContent);
    } else if (type === 'photo') {
        const img = document.createElement('img');
        img.src = content;
        img.alt = '';
        item.appendChild(img);
    } else if (type === 'video') {
        const video = document.createElement('video');
        video.src = content;
        video.controls = true;
        video.style.maxWidth = '100%';
        item.appendChild(video);
    }

    item.addEventListener('mouseenter', function() {
        if (clickedItem !== item) {
            focusedItem = item;
            item.classList.add('focused');
        }
    });

    item.addEventListener('mouseleave', function() {
        if (focusedItem === item) {
            focusedItem = null;
            item.classList.remove('focused');
        }
    });

    item.addEventListener('click', function(e) {
        e.stopPropagation();

        if (clickedItem === item) {
            // Unfocus if clicking the same item
            item.classList.remove('clicked');
            clickedItem = null;

            // Return to original position
            var baseX = parseFloat(item.getAttribute('data-base-x'));
            var baseY = parseFloat(item.getAttribute('data-base-y'));
            item.style.left = baseX + 'px';
            item.style.top = baseY + 'px';
        } else {
            // Unfocus previous item if any
            if (clickedItem) {
                clickedItem.classList.remove('clicked');
                var prevBaseX = parseFloat(clickedItem.getAttribute('data-base-x'));
                var prevBaseY = parseFloat(clickedItem.getAttribute('data-base-y'));
                clickedItem.style.left = prevBaseX + 'px';
                clickedItem.style.top = prevBaseY + 'px';
            }

            // Focus new item
            clickedItem = item;
            item.classList.add('clicked');
            centerItem(item);
        }
    });

    container.appendChild(item);
    contentItems.push(item);
}

function animate() {
    if (!animationRunning) return;

    for (let i = 0; i < contentItems.length; i++) {
        const item = contentItems[i];
        if (item === focusedItem || item === clickedItem) continue;

        let baseX = parseFloat(item.getAttribute('data-base-x'));
        let baseY = parseFloat(item.getAttribute('data-base-y'));
        let velocityX = parseFloat(item.getAttribute('data-velocity-x'));
        let velocityY = parseFloat(item.getAttribute('data-velocity-y'));
        let wigglePhase = parseFloat(item.getAttribute('data-wiggle-phase'));

        // Update base position
        baseX += velocityX;
        baseY += velocityY;

        // Bounce off edges
        const itemWidth = item.offsetWidth || 300;
        const itemHeight = item.offsetHeight || 200;
        const maxX = window.innerWidth - itemWidth;
        const maxY = window.innerHeight - itemHeight;

        if (baseX <= 0 || baseX >= maxX) {
            velocityX *= -1;
            baseX = Math.max(0, Math.min(maxX, baseX));
        }
        if (baseY <= 0 || baseY >= maxY) {
            velocityY *= -1;
            baseY = Math.max(0, Math.min(maxY, baseY));
        }

        // Wiggle effect
        wigglePhase += 0.05;
        const wiggleX = Math.sin(wigglePhase) * 3;
        const wiggleY = Math.cos(wigglePhase * 1.3) * 3;
        const wiggleRotate = Math.sin(wigglePhase * 0.7) * 2;

        // Apply position and wiggle
        item.style.left = (baseX + wiggleX) + 'px';
        item.style.top = (baseY + wiggleY) + 'px';
        item.style.transform = 'rotate(' + wiggleRotate + 'deg)';

        // Update attributes
        item.setAttribute('data-base-x', baseX);
        item.setAttribute('data-base-y', baseY);
        item.setAttribute('data-velocity-x', velocityX);
        item.setAttribute('data-velocity-y', velocityY);
        item.setAttribute('data-wiggle-phase', wigglePhase);
    }

    requestAnimationFrame(animate);
}

// Click outside to unfocus
document.addEventListener('click', function(e) {
    if (clickedItem && e.target.closest('.content-item') === null) {
        clickedItem.classList.remove('clicked');
        var baseX = parseFloat(clickedItem.getAttribute('data-base-x'));
        var baseY = parseFloat(clickedItem.getAttribute('data-base-y'));
        clickedItem.style.left = baseX + 'px';
        clickedItem.style.top = baseY + 'px';
        clickedItem = null;
    }
});

// Load posts from JSON file
function loadPosts() {
    fetch('posts.json')
        .then(function(response) {
            if (!response.ok) {
                throw new Error('Failed to load posts');
            }
            return response.json();
        })
        .then(function(posts) {
            posts.forEach(function(post) {
                createContentItem(post.type, post.content);
            });

            // Wait for next frame to ensure elements are rendered
            setTimeout(function() {
                animationRunning = true;
                animate();
            }, 100);
        })
        .catch(function(error) {
            console.error('Error loading posts:', error);
        });
}

// Initialize on page load
window.addEventListener('DOMContentLoaded', function() {
    loadPosts();
});
