// Visitor counter
let visitorCount = Math.floor(Math.random() * 9999) + 1000;
document.getElementById('visitor-count').textContent = visitorCount;

// Array to store all content items
let contentItems = [];

// Random position generator
function getRandomPosition() {
    const container = document.getElementById('content-container');
    const containerRect = container.getBoundingClientRect();

    const maxX = Math.max(400, containerRect.width - 300);
    const maxY = Math.max(400, containerRect.height - 300);

    return {
        top: Math.random() * maxY,
        left: Math.random() * maxX
    };
}

// Slight random rotation for variety
function getRandomRotation() {
    return (Math.random() * 4 - 2); // -2 to 2 degrees
}

// Create a content item
function createContentItem(type, content) {
    const container = document.getElementById('content-container');
    const item = document.createElement('div');
    item.className = `content-item ${type}-item`;

    // Apply random positioning
    const pos = getRandomPosition();
    const rotation = getRandomRotation();

    item.style.top = pos.top + 'px';
    item.style.left = pos.left + 'px';
    item.style.transform = `rotate(${rotation}deg)`;

    // Add close button
    const closeBtn = document.createElement('button');
    closeBtn.className = 'close-btn';
    closeBtn.innerHTML = '×';
    closeBtn.onclick = function() {
        item.remove();
        contentItems = contentItems.filter(i => i !== item);
    };
    item.appendChild(closeBtn);

    // Add content based on type
    switch(type) {
        case 'text':
            const textContent = document.createElement('p');
            textContent.textContent = content;
            item.appendChild(textContent);
            break;

        case 'photo':
            const img = document.createElement('img');
            img.src = content;
            img.alt = 'Image';
            img.onerror = function() {
                item.innerHTML = '<p style="color: #999;">Image failed to load</p>';
            };
            item.appendChild(img);
            break;

        case 'audio':
            const audioLabel = document.createElement('div');
            audioLabel.className = 'audio-label';
            audioLabel.textContent = 'audio';
            const audio = document.createElement('audio');
            audio.controls = true;
            audio.src = content;
            item.appendChild(audioLabel);
            item.appendChild(audio);
            break;

        case 'video':
            const videoLabel = document.createElement('div');
            videoLabel.className = 'video-label';
            videoLabel.textContent = 'video';
            const video = document.createElement('video');
            video.controls = true;
            video.src = content;
            video.style.maxWidth = '100%';
            item.appendChild(videoLabel);
            item.appendChild(video);
            break;
    }

    // Make item draggable
    makeDraggable(item);

    container.appendChild(item);
    contentItems.push(item);

    // Fade in animation
    item.style.opacity = '0';
    setTimeout(() => {
        item.style.transition = 'opacity 0.5s';
        item.style.opacity = '1';
    }, 10);
}

// Make elements draggable
function makeDraggable(element) {
    let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;

    element.onmousedown = dragMouseDown;

    function dragMouseDown(e) {
        // Don't drag if clicking close button
        if (e.target.className === 'close-btn') return;

        e.preventDefault();
        pos3 = e.clientX;
        pos4 = e.clientY;
        document.onmouseup = closeDragElement;
        document.onmousemove = elementDrag;

        element.style.zIndex = 1000;
    }

    function elementDrag(e) {
        e.preventDefault();
        pos1 = pos3 - e.clientX;
        pos2 = pos4 - e.clientY;
        pos3 = e.clientX;
        pos4 = e.clientY;
        element.style.top = (element.offsetTop - pos2) + "px";
        element.style.left = (element.offsetLeft - pos1) + "px";
    }

    function closeDragElement() {
        document.onmouseup = null;
        document.onmousemove = null;
        element.style.zIndex = 'auto';
    }
}

// Add text
function addText() {
    const input = document.getElementById('text-input');
    if (input.value.trim()) {
        createContentItem('text', input.value);
        input.value = '';
    }
}

// Add photo from URL
function addPhoto() {
    const input = document.getElementById('photo-input');
    if (input.value.trim()) {
        createContentItem('photo', input.value);
        input.value = '';
    }
}

// Add audio from URL
function addAudio() {
    const input = document.getElementById('audio-input');
    if (input.value.trim()) {
        createContentItem('audio', input.value);
        input.value = '';
    }
}

// Add video from URL
function addVideo() {
    const input = document.getElementById('video-input');
    if (input.value.trim()) {
        createContentItem('video', input.value);
        input.value = '';
    }
}

// Handle file uploads
document.getElementById('photo-file').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = function(event) {
            createContentItem('photo', event.target.result);
        };
        reader.readAsDataURL(file);
    }
    this.value = '';
});

document.getElementById('audio-file').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file && file.type.startsWith('audio/')) {
        const reader = new FileReader();
        reader.onload = function(event) {
            createContentItem('audio', event.target.result);
        };
        reader.readAsDataURL(file);
    }
    this.value = '';
});

document.getElementById('video-file').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file && file.type.startsWith('video/')) {
        const reader = new FileReader();
        reader.onload = function(event) {
            createContentItem('video', event.target.result);
        };
        reader.readAsDataURL(file);
    }
    this.value = '';
});

// Clear all content
function clearAll() {
    const container = document.getElementById('content-container');
    container.innerHTML = '';
    contentItems = [];
}

// Click counter to increment
document.getElementById('visitor-count').addEventListener('click', function() {
    visitorCount++;
    this.textContent = visitorCount;
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter to add text
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const textInput = document.getElementById('text-input');
        if (textInput === document.activeElement && textInput.value.trim()) {
            addText();
        }
    }
});
