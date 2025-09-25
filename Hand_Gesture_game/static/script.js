// ✅ Global click sound handler early definition
function playClickSound() {
    const audio = document.getElementById('clickSound');  // unified consistent ID
    if (audio) {
        audio.currentTime = 0;
        audio.play().catch(e => console.warn("Click sound error:", e));
    }
}

// ✅ Global event listener for all buttons
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('button').forEach(button => {
        button.addEventListener('click', playClickSound);
    });
});


// A Witcher's Story - JavaScript Logic
// Enhanced Interactive Story System with Twee File Integration

// --- Global Variables ---
let currentPassage = 'Start';
let currentOptions = [];
let gesturePollingInterval = null;
let lastProcessedGestureId = null;
let lastGestureTime = 0;
let apiConnected = false;
let currentMode = 'gestures';
let debugMode = false;
let storyCache = {}; // Cache for story passages

// Gesture cooldown
const GESTURE_COOLDOWN = 3000; // 3 seconds

// --- DOM Elements ---
const storyText = document.getElementById('story-text');
const storyImage = document.getElementById('story-image');
const optionsContainer = document.getElementById('options-container');
const gestureIndicator = document.getElementById('gesture-indicator');
const apiStatus = document.getElementById('api-status');
const settingsFrame = document.getElementById('settings-frame');
const volumeSlider = document.getElementById('volume-slider');
const volumeDisplay = document.getElementById('volume-display');
const modeSelect = document.getElementById('mode-select');
const statusDot = document.getElementById('status-dot');

// Debug information
console.log('DOM Elements Check:');
console.log('story-text:', document.getElementById('story-text'));
console.log('options-container:', document.getElementById('options-container'));
console.log('start-button:', document.getElementById('start-button'));
console.log("✅ script.js is loaded");


// --- Initialization ---
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    startGesturePolling();
    updateApiStatus();
    loadPassageFromAPI('Start');

    // --- GLOBAL: Play click sound on any button ---
// removed duplicate button click sound handler

    // Debug information
    console.log('🐺 A Witcher\'s Story - Twee Edition Loaded');
});

// --- Enhanced Features ---

// Start gesture
function startGesturePolling() {
    if (gesturePollingInterval) {
        clearInterval(gesturePollingInterval);
    }
    
    // Check for new gestures every 1 second
    gesturePollingInterval = setInterval(checkForNewGesture, 1000);
    console.log('Started gesture');
}

// Check for new gestures
function checkForNewGesture() {
    // Only proceed if API is connected
    if (!apiConnected) {
        return;
    }
    
    // Get the latest gesture from the API
    fetch('/api/gesture/latest')
        .then(response => response.json())
        .then(data => {
            // Process the gesture if it's new and valid
            if (data && data.gesture && data.id !== lastProcessedGestureId) {
                processGesture(data);
                lastProcessedGestureId = data.id;
            }
        })
        .catch(error => {
            console.error('Error fetching gesture:', error);
            apiConnected = false;
            updateApiStatus();
        });
}

// Process a detected gesture or emotion
function processGesture(gestureData) {
    const now = Date.now();
    
    // Enforce cooldown to prevent rapid gesture selection
    if (now - lastGestureTime < GESTURE_COOLDOWN) {
        return;
    }
    
    lastGestureTime = now;
    const gesture = gestureData.gesture.toLowerCase();
    
    // Map gestures/emotions to option indices
    let optionIndex = -1;
    
    if (currentMode === 'emotions') {
        // Map hand gestures to option indices
        if (gesture.includes('thumbs_up') || gesture.includes('thumbs up')) {
            optionIndex = 0;
        } else if (gesture.includes('thumbs_down') || gesture.includes('thumbs down')) {
            optionIndex = 1;
        } else if (gesture.includes('victory') || gesture.includes('peace')) {
            optionIndex = 2;
        } else if (gesture.includes('pointing') || gesture.includes('pointing up')) {
            optionIndex = 3;
        }
    }
    
    // Execute the selected option if valid
    if (optionIndex >= 0 && optionIndex < currentOptions.length) {
        showGestureIndicator(`Detected: ${gestureData.gesture} (Option ${optionIndex + 1})`, 'success');
        
        // Short delay for user to see what was detected
        setTimeout(() => {
            selectOption(currentOptions[optionIndex].destination);
        }, 1000);
    }
}

// Typewriter effect for story text
async function typewriterEffect(element, text, speed = 30) {
    element.textContent = '';
    element.classList.add('fade-in');

    for (let i = 0; i < text.length; i++) {
        element.textContent += text.charAt(i);
        await new Promise(resolve => setTimeout(resolve, speed));
    }
}

// Load passage from the backend API
async function loadPassageFromAPI(passageId) {
    // Show loading indicator
    showGestureIndicator(`Loading passage: ${passageId}`, 'info');
    console.log(`Loading passage from API: ${passageId}`);
    
    try {
        // Check cache first
        if (storyCache[passageId] && !debugMode) {
            console.log(`Using cached passage data for: ${passageId}`);
            processPassage(storyCache[passageId]);
            return;
        }
        
        // Fetch from API if not in cache
        console.log(`Fetching passage from server: ${passageId}`);
        const response = await fetch(`/api/passage?name=${encodeURIComponent(passageId)}`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'Cache-Control': 'no-cache'
            }
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error(`Server error (${response.status}): ${errorText}`);
            throw new Error(`Failed to load passage: ${response.status}`);
        }
        
        const passageData = await response.json();
        console.log('Received passage data:', passageData);
        
        if (passageData.error) {
            throw new Error(`Server error: ${passageData.error}`);
        }
        
        // Cache the passage
        storyCache[passageId] = passageData;
        
        // Process the loaded passage
        processPassage(passageData);
    } catch (error) {
        console.error('Error loading passage:', error);
        showGestureIndicator(`Error loading story: ${error.message}. Please try again.`, 'error');
        
        // Re-enable option buttons
        const buttons = document.querySelectorAll('.option-button');
        buttons.forEach(button => {
            button.disabled = false;
            button.classList.remove('disabled');
        });
    }
    
    // Try to play the click sound if it exists
    const clickSound = document.getElementById('click-sound');
    if (clickSound) {
        clickSound.currentTime = 0;
        clickSound.play().catch(error => {
            console.warn('Could not play click sound:', error);
        });
    }
}

// Helper functions for gesture indicators
function showGestureIndicator(message, type = 'info') {
    const indicator = document.getElementById('gesture-indicator');
    if (indicator) {
        indicator.textContent = message;
        indicator.className = `gesture-indicator ${type}`;
        indicator.style.display = 'block';
    }
}

function hideGestureIndicator() {
    const indicator = document.getElementById('gesture-indicator');
    if (indicator) {
        indicator.style.display = 'none';
    }
}

// Initialize variables
let currentOptions = [];
let storyCache = {};
let debugMode = false;

// Document ready function
document.addEventListener('DOMContentLoaded', function() {
    console.log('Document ready, initializing story...');
    
    // Initialize by loading the Start passage
    loadPassageFromAPI('Start');
    
    // Set up start button
    const startButton = document.getElementById('start-button');
    if (startButton) {
        startButton.addEventListener('click', function() {
            playClickSound();
            loadPassageFromAPI('Start');
        });
    }
});

// Add processPassage function if it doesn't exist
function processPassage(passageData) {
    console.log('Processing passage:', passageData);
    
    // Update the story text
    const storyTextElement = document.getElementById('story-text');
    if (storyTextElement) {
        storyTextElement.innerHTML = passageData.text.replace(/\n/g, '<br>');
        storyTextElement.classList.add('fade-in');
        setTimeout(() => storyTextElement.classList.remove('fade-in'), 1000);
    }
    
    // Update story image if applicable
    updateStoryImage(passageData.name, passageData.has_image);
    
    // Add options for the user to select
    populateOptionButtons(passageData.options);
    
    // Update current options global variable
    currentOptions = passageData.options || [];
    
    // Update page title
    document.title = `A Witcher's Tale: ${passageData.name}`;
    
    // Hide the loading indicator
    hideGestureIndicator();
    
    // Update URL hash for bookmarking
    window.location.hash = passageData.name;
    
    // Play ambient sound based on passage name
    playAmbientSound(passageData.name);
}

// Helper function to update the story image
function updateStoryImage(passageName, hasImage) {
    const storyImage = document.getElementById('story-image');
    if (storyImage) {
        if (hasImage) {
            storyImage.src = `/images/${encodeURIComponent(passageName)}.jpg`;
            storyImage.alt = passageName;
        } else {
            // Use a default placeholder image
            storyImage.src = "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgdmlld0JveD0iMCAwIDQwMCAzMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSI0MDAiIGhlaWdodD0iMzAwIiBmaWxsPSIjMWExYTFhIi8+CjxjaXJjbGUgY3g9IjIwMCIgY3k9IjEwMCIgcj0iNDAiIGZpbGw9IiNiNmI5NDMiIG9wYWNpdHk9IjAuMyIvPgo8cGF0aCBkPSJNMTUwIDIwMEwyNTAgMjAwTDIwMCAxNTBaIiBmaWxsPSIjOGIwMDAwIiBvcGFjaXR5PSIwLjQiLz4KPHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHg9IjE4MCIgeT0iMjMwIiB2aWV3Qm94PSIwIDAgMjQgMjQiIGZpbGw9Im5vbmUiIHN0cm9rZT0iI2I2Yjk0MyIgc3Ryb2tlLXdpZHRoPSIyIj4KPHA+R2VyYWx0IG9mIFJpdmlhPC9wPgo8cD5UaGUgV2hpdGUgV29sZjwvcD4KPC9zdmc+Cjx0ZXh0IHg9IjIwMCIgeT0iMjcwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSIjYjZiOTQzIiBmb250LWZhbWlseT0ic2VyaWYiIGZvbnQtc2l6ZT0iMTRweCIgZm9udC13ZWlnaHQ9ImJvbGQiPldpdGNoZXIgVGFsZTwvdGV4dD4KPHRleHQgeD0iMjAwIiB5PSIyODUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZpbGw9IiNlMGUwZTAiIGZvbnQtZmFtaWx5PSJzZXJpZiIgZm9udC1zaXplPSIxMHB4IiBmb250LXN0eWxlPSJpdGFsaWMiPkFuIGludGVyYWN0aXZlIGFkdmVudHVyZTwvdGV4dD4KPC9zdmc+";
            storyImage.alt = "Witcher Tale";
        }
    }
}



// Process a loaded passage
async function processPassage(passage) {
    if (!passage) {
        console.error('Invalid passage data');
        showGestureIndicator('This path leads into uncharted territory...', 'warning');
        return;
    }
    
    currentPassage = passage.name;
    currentOptions = passage.options || [];
    
    // Show loading indicator
    showGestureIndicator(`Entering: ${passage.name}`, 'info');
    
    // Simulate slight delay for immersion
    await delay(800);
    
    // Update the story image if available
    if (passage.has_image) {
        storyImage.src = `/images/${encodeURIComponent(passage.name)}.jpg`;
        storyImage.alt = passage.name;
    } else {
        // Use default placeholder image
        storyImage.src = "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgdmlld0JveD0iMCAwIDQwMCAzMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSI0MDAiIGhlaWdodD0iMzAwIiBmaWxsPSIjMWExYTFhIi8+CjxjaXJjbGUgY3g9IjIwMCIgY3k9IjEwMCIgcj0iNDAiIGZpbGw9IiNiNmI5NDMiIG9wYWNpdHk9IjAuMyIvPgo8cGF0aCBkPSJNMTUwIDIwMEwyNTAgMjAwTDIwMCAxNTBaIiBmaWxsPSIjOGIwMDAwIiBvcGFjaXR5PSIwLjQiLz4KPHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHg9IjE4MCIgeT0iMjMwIiB2aWV3Qm94PSIwIDAgMjQgMjQiIGZpbGw9Im5vbmUiIHN0cm9rZT0iI2I2Yjk0MyIgc3Ryb2tlLXdpZHRoPSIyIj4KPHA+VmlsbGFnZSBvZiBPeGVuZnVydDwvcD4KPHA+R2VyYWx0J3MgQWR2ZW50dXJlIEJlZ2luczwvcD4KPC9zdmc+Cjx0ZXh0IHg9IjIwMCIgeT0iMjcwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSIjYjZiOTQzIiBmb250LWZhbWlseT0ic2VyaWYiIGZvbnQtc2l6ZT0iMTRweCIgZm9udC13ZWlnaHQ9ImJvbGQiPldpdGNoZXIncyBUYWxlPC90ZXh0Pgo8dGV4dCB4PSIyMDAiIHk9IjI4NSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZmlsbD0iI2UwZTBlMCIgZm9udC1mYW1pbHk9InNlcmlmIiBmb250LXNpemU9IjEwcHgiIGZvbnQtc3R5bGU9Iml0YWxpYyI+QSB0YWxlIG9mIG1vbnN0ZXJzIGFuZCBtZW48L3RleHQ+Cjwvc3ZnPg==";
        storyImage.alt = passage.name;
    }
    
    // Use typewriter effect for story text
    await typewriterEffect(storyText, passage.text);
    
    // Create option buttons with animation delays
    createOptionButtonsEnhanced();
    
    hideGestureIndicator();
}

// Enhanced option button creation with animations
function createOptionButtonsEnhanced() {
    optionsContainer.innerHTML = '';
    console.log(`Creating ${currentOptions.length} option buttons`);

    currentOptions.forEach((option, index) => {
        const button = document.createElement('button');
        button.className = 'option-button fade-in';
        button.textContent = `${index + 1}. ${option.text}`;
        button.style.animationDelay = `${index * 0.1}s`;
        
        // Add data attribute to help with debugging
        button.dataset.destination = option.destination;
        button.dataset.optionIndex = index;

        // Use onclick attribute as a backup in case addEventListener fails
        button.setAttribute('onclick', `handleOptionClick('${option.destination}')`);
        
        // Add the event listener
        button.addEventListener('click', function(e) {
            e.preventDefault();
            console.log(`Option ${index + 1} clicked, destination: ${option.destination}`);
            playClickSound();
            selectOption(option.destination);
        });

        optionsContainer.appendChild(button);
    });
}

// Global function to handle option clicks as a backup method
function handleOptionClick(destination) {
    console.log(`Option clicked via onclick attribute, destination: ${destination}`);
    playClickSound();
    selectOption(destination);
}

function populateOptionButtons(options) {
    console.log('Populating option buttons:', options);
    const optionsContainer = document.getElementById('options-container');
    optionsContainer.innerHTML = ''; // Clear existing options
    
    if (!options || options.length === 0) {
        // If no options, add a default "continue" option that reloads the current passage
        const endButton = document.createElement('button');
        endButton.className = 'option-button fade-in';
        endButton.textContent = 'Return to Start';
        endButton.onclick = function() { handleOptionClick('Start'); };
        optionsContainer.appendChild(endButton);
        return;
    }
    
    // Add each option as a button
    options.forEach((option, index) => {
        const button = document.createElement('button');
        button.className = 'option-button fade-in';
        button.style.animationDelay = `${index * 0.2}s`;
        button.textContent = `${index + 1}. ${option.text}`;
        
        // Add onclick handler directly to the button
        button.onclick = function() {
            handleOptionClick(option.destination);
        };
        
        optionsContainer.appendChild(button);
    });
}

// Enhanced option selection with transition effects
function selectOption(destination) {
    if (destination) {
        console.log(`Selecting option with destination: ${destination}`);
        showGestureIndicator(`Traveling to: ${destination}`, 'success');
        
        // Disable all option buttons temporarily to prevent multiple clicks
        const buttons = document.querySelectorAll('.option-button');
        buttons.forEach(button => {
            button.disabled = true;
            button.classList.add('disabled');
        });
        
        setTimeout(() => {
            loadPassageFromAPI(destination);
        }, 1000);
    } else {
        console.error('Invalid destination provided to selectOption function');
        showGestureIndicator('This path leads into uncharted territory...', 'warning');
        setTimeout(hideGestureIndicator, 3000);
    }
}

function fetchApiStatus() {
  fetch('/api/status')
    .then(response => response.json())
    .then(data => {
      apiConnected = data.api_connected;
      const statusBox = document.getElementById('apiStatus');
      if (apiConnected) {
        statusBox.textContent = "🟢 Witcher Senses Active – API Connected";
        statusBox.classList.remove('disconnected');
        statusBox.classList.add('connected');
      } else {
        statusBox.textContent = `🔴 Witcher Senses Dormant – API Disconnected`;
        statusBox.classList.remove('connected');
        statusBox.classList.add('disconnected');
      }
    })
    .catch(error => {
      const statusBox = document.getElementById('apiStatus');
      statusBox.textContent = "🔴 Witcher Senses Dormant – Network Error";
      statusBox.classList.remove('connected');
      statusBox.classList.add('disconnected');
    });
}


// Poll every 5 seconds
setInterval(fetchApiStatus, 5000);
window.addEventListener('DOMContentLoaded', fetchApiStatus);



// --- Event Listeners ---
function setupEventListeners() {
    // Start/Restart button
    document.getElementById('start-button').addEventListener('click', function() {
        playClickSound();
        loadPassageFromAPI('Start');
    });

    // Settings toggle
    document.getElementById('settings-button').addEventListener('click', function() {
        playClickSound();
        toggleSettings();
    });

    // Reconnect API
    document.getElementById('reconnect-button').addEventListener('click', function() {
        playClickSound();
        showGestureIndicator('Reconnecting emotion/gesture API...', 'info');
        
        // Try to reconnect to the API
        fetch('/api/reconnect')
            .then(response => response.json())
            .then(data => {
                apiConnected = data.connected;
                updateApiStatus();
                
                if (apiConnected) {
                    showGestureIndicator('API Connected! Gesture control active.', 'success');
                } else {
                    showGestureIndicator('API Disconnected. Using demo mode.', 'warning');
                }
                
                setTimeout(hideGestureIndicator, 2000);
            })
            .catch(error => {
                console.error('Error reconnecting:', error);
                apiConnected = false;
                updateApiStatus();
                showGestureIndicator('Failed to connect to API. Using demo mode.', 'error');
                setTimeout(hideGestureIndicator, 2000);
            });
    });
    
    // Debug button
    document.getElementById('debug-button').addEventListener('click', function() {
        playClickSound();
        debugMode = !debugMode;
        
        if (debugMode) {
            fetch('/api/debug/endpoints')
                .then(response => response.json())
                .then(data => {
                    console.log('Debug Info:', data);
                    showGestureIndicator('Debug info in console. Press F12 to view.', 'info');
                    setTimeout(hideGestureIndicator, 3000);
                })
                .catch(error => {
                    console.error('Debug error:', error);
                });
        } else {
            showGestureIndicator('Debug mode disabled', 'info');
            setTimeout(hideGestureIndicator, 2000);
        }
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Number keys for options
        const num = parseInt(e.key);
        if (num >= 1 && num <= currentOptions.length) {
            e.preventDefault();
            selectOption(currentOptions[num - 1].destination);
        }

        // Ctrl+R for restart
        if (e.ctrlKey && e.key === 'r') {
            e.preventDefault();
            loadPassageFromAPI('Start');
        }

        // Ctrl+S for settings
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            toggleSettings();
        }

        // Escape to close settings
        if (e.key === 'Escape') {
            settingsFrame.classList.remove('active');
        }
    });

    // Volume slider
    volumeSlider.addEventListener('input', function() {
        volumeDisplay.textContent = this.value + '%';
        
        // Send volume update to server
        fetch('/api/volume', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                volume: parseInt(this.value)
            }),
        }).catch(error => console.error('Error updating volume:', error));
    });

    // Mode select
    modeSelect.addEventListener('change', function() {
        currentMode = this.value;
        showGestureIndicator(`Switched to ${this.value} mode`, 'info');
        
        // Update mode on server
        fetch('/api/switch_mode', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                mode: this.value
            }),
        }).catch(error => console.error('Error updating mode:', error));
        
        setTimeout(hideGestureIndicator, 2000);
    });
    
    // Test API Connection
    document.getElementById('test-api-connection').addEventListener('click', function() {
        playClickSound();
        showGestureIndicator('Testing API connection...', 'info');
        
        fetch('/api/status')
            .then(response => response.json())
            .then(data => {
                apiConnected = data.api_connected;
                updateApiStatus();
                
                const statusMessage = apiConnected 
                    ? 'API Connected! Gesture control active.' 
                    : `API Disconnected: ${data.api_error}`;
                    
                showGestureIndicator(statusMessage, apiConnected ? 'success' : 'warning');
                setTimeout(hideGestureIndicator, 3000);
            })
            .catch(error => {
                console.error('Error testing API:', error);
                apiConnected = false;
                updateApiStatus();
                showGestureIndicator('Error testing API connection', 'error');
                setTimeout(hideGestureIndicator, 3000);
            });
    });
}

// --- Utility Functions ---
function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function showGestureIndicator(message, type = 'info') {
    gestureIndicator.textContent = message;
    gestureIndicator.className = `gesture-indicator show ${type}`;
}

function hideGestureIndicator() {
    gestureIndicator.classList.remove('show');
}







function updateApiStatus() {
    const apiStatusElement = document.getElementById('api-status');
    
    if (apiConnected) {
        apiStatusElement.textContent = '✨ Witcher Senses Active - Medallion Humming';
        apiStatusElement.className = 'api-status connected';
    } else {
        apiStatusElement.textContent = '💤 Witcher Senses Dormant - Manual Control';
        apiStatusElement.className = 'api-status disconnected';
    }
    
    // Check API status on load
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            apiConnected = data.api_connected;
            updateUIForApiStatus();
        })
        .catch(error => {
            console.error('Error checking API status:', error);
            apiConnected = false;
            updateUIForApiStatus();
        });
}




function updateUIForApiStatus() {
    const apiStatusElement = document.getElementById('api-status');
    const gestureIndicatorElement = document.getElementById('gesture-indicator');

    if (apiConnected) {
        apiStatusElement.textContent = '🟢 Witcher Senses Active – API Connected';
        apiStatusElement.className = 'api-status connected';
        gestureIndicatorElement.innerHTML = `
            <span class="gesture-icon">🧠</span>
            <span class="gesture-text">Gesture control is active. Use your signs, witcher.</span>
        `;
    } else {
        apiStatusElement.textContent = '🔴 Witcher Senses Dormant – API Disconnected';
        apiStatusElement.className = 'api-status disconnected';
        gestureIndicatorElement.innerHTML = `
            <span class="gesture-icon">💤</span>
            <span class="gesture-text">No connection. Meditate or check your potions (API).</span>
        `;
    }
}