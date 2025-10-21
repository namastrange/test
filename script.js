let contentItems = [];

function getRandomPosition() {
    const container = document.getElementById('content-container');
    const containerRect = container.getBoundingClientRect();

    const maxX = Math.max(300, containerRect.width - 320);
    const maxY = Math.max(300, containerRect.height - 300);

    return {
        top: Math.random() * maxY,
        left: Math.random() * maxX
    };
}

function createContentItem(type, content) {
    const container = document.getElementById('content-container');
    const item = document.createElement('div');
    item.className = `content-item ${type}-item`;

    const pos = getRandomPosition();
    item.style.top = pos.top + 'px';
    item.style.left = pos.left + 'px';

    const closeBtn = document.createElement('button');
    closeBtn.className = 'close-btn';
    closeBtn.innerHTML = '×';
    closeBtn.onclick = function() {
        item.remove();
        contentItems = contentItems.filter(i => i !== item);
    };
    item.appendChild(closeBtn);

    switch(type) {
        case 'text':
            const textContent = document.createElement('p');
            textContent.textContent = content;
            item.appendChild(textContent);
            break;

        case 'photo':
            const img = document.createElement('img');
            img.src = content;
            img.alt = '';
            img.onerror = function() {
                item.innerHTML = '<p>image failed to load</p>';
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
            item.appendChild(videoLabel);
            item.appendChild(video);
            break;
    }

    makeDraggable(item);
    container.appendChild(item);
    contentItems.push(item);
}

function makeDraggable(element) {
    let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;

    element.onmousedown = dragMouseDown;

    function dragMouseDown(e) {
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

function addText() {
    const input = document.getElementById('text-input');
    if (input.value.trim()) {
        createContentItem('text', input.value);
        input.value = '';
    }
}

function addPhoto() {
    const input = document.getElementById('photo-input');
    if (input.value.trim()) {
        createContentItem('photo', input.value);
        input.value = '';
    }
}

function addAudio() {
    const input = document.getElementById('audio-input');
    if (input.value.trim()) {
        createContentItem('audio', input.value);
        input.value = '';
    }
}

function addVideo() {
    const input = document.getElementById('video-input');
    if (input.value.trim()) {
        createContentItem('video', input.value);
        input.value = '';
    }
}

function clearAll() {
    const container = document.getElementById('content-container');
    container.innerHTML = '';
    contentItems = [];
}

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

document.addEventListener('keydown', function(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const textInput = document.getElementById('text-input');
        if (textInput === document.activeElement && textInput.value.trim()) {
            addText();
        }
    }
});
