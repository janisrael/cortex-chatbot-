// Appearance Tab JavaScript
let appearanceConfig = {
    description: 'Your friendly assistant',
    primary_color: {
        type: 'solid',
        value: '#1093B2',
        contrast_text: '#ffffff'
    },
    avatar: {
        type: 'preset',
        value: 'preset_1',
        fallback: 'ui-avatars'
    },
    suggested_messages: []
};

let gradientColors = [];
let messageCounter = 0;

// Initialize appearance tab
async function initializeAppearance() {
    // Load config first (await it)
    await loadAppearanceConfig();
    // Then setup UI components
    setupDescriptionInput();
    setupColorPicker();
    setupGradientBuilder();
    setupAvatarSelection();
    setupSuggestedMessages();
    setupSaveButton();
    updatePreview();
}

// Load appearance configuration
async function loadAppearanceConfig() {
    try {
        const response = await fetch('/api/user/chatbot-config');
        const data = await response.json();
        const config = data.config || data;
        
        console.log('📥 Loaded config from API:', {
            primary_color: config.primary_color,
            primary_color_type: typeof config.primary_color,
            primary_color_is_string: typeof config.primary_color === 'string',
            primary_color_is_object: typeof config.primary_color === 'object' && config.primary_color !== null
        });
        
        // Load bot name for preview
        if (config.bot_name) {
            const botNameEl = document.getElementById('previewBotName');
            if (botNameEl) botNameEl.textContent = config.bot_name;
        }
        
        // Load description
        if (config.short_info || config.description) {
            appearanceConfig.description = config.short_info || config.description || 'Your friendly assistant';
        } else {
            appearanceConfig.description = 'Your friendly assistant';
        }
        
        // Update description input
        const descriptionInput = document.getElementById('chatbotDescription');
        if (descriptionInput) {
            descriptionInput.value = appearanceConfig.description;
        }
        
        // Load primary color
        if (config.primary_color) {
            if (typeof config.primary_color === 'string') {
                // Legacy format - convert to new format
                console.log('⚠️ Primary color is string (legacy format), converting to solid');
                appearanceConfig.primary_color = {
                    type: 'solid',
                    value: config.primary_color,
                    contrast_text: calculateContrastText(config.primary_color)
                };
            } else if (typeof config.primary_color === 'object' && config.primary_color !== null) {
                // New format - should have type and value
                console.log('✅ Primary color is object:', config.primary_color);
                appearanceConfig.primary_color = config.primary_color;
                
                // Ensure it has type field
                if (!appearanceConfig.primary_color.type) {
                    console.warn('⚠️ Primary color object missing type field, defaulting to solid');
                    appearanceConfig.primary_color.type = 'solid';
                }
            } else {
                console.warn('⚠️ Primary color is unexpected type:', typeof config.primary_color);
                appearanceConfig.primary_color = {
                    type: 'solid',
                    value: '#0891b2',
                    contrast_text: '#ffffff'
                };
            }
        } else {
            console.log('ℹ️ No primary color in config, using default');
            // Default primary color
            appearanceConfig.primary_color = {
                type: 'solid',
                value: '#1093B2',
                contrast_text: '#ffffff'
            };
        }
        
        console.log('✅ Final appearanceConfig.primary_color:', appearanceConfig.primary_color);
        
        // Load avatar
        if (config.avatar) {
            appearanceConfig.avatar = config.avatar;
        } else {
            // Default avatar
            appearanceConfig.avatar = {
                type: 'preset',
                value: 'avatar_1',
                name: 'cort',
                fallback: 'ui-avatars'
            };
        }
        
        // Load suggested messages
        console.log('📥 Loading suggested messages:', config.suggested_messages);
        if (config.suggested_messages && Array.isArray(config.suggested_messages) && config.suggested_messages.length > 0) {
            appearanceConfig.suggested_messages = config.suggested_messages;
            console.log('✅ Loaded suggested messages from config:', appearanceConfig.suggested_messages.length);
        } else {
            // Default messages
            appearanceConfig.suggested_messages = [
                { id: 'default_1', text: 'What can you help me with?', order: 1 },
                { id: 'default_2', text: 'Tell me more', order: 2 },
                { id: 'default_3', text: 'How can I get started?', order: 3 }
            ];
            console.log('⚠️ Using default suggested messages');
        }
        
        // Update UI - but wait a bit for DOM to be ready
        setTimeout(() => {
            console.log('🔄 Updating appearance UI with config:', {
                colorType: appearanceConfig.primary_color.type,
                colorValue: appearanceConfig.primary_color.value ? (appearanceConfig.primary_color.value.substring(0, 50) + '...') : 'null',
                description: appearanceConfig.description,
                avatar: appearanceConfig.avatar
            });
            updateColorUI();
            updateAvatarUI();
            updateSuggestedMessagesUI();
            updatePreview();
        }, 150);
    } catch (error) {
        console.error('Failed to load appearance config:', error);
    }
}

// Setup color picker
function setupColorPicker() {
    const solidColorPicker = document.getElementById('solidColorPicker');
    const solidColorInput = document.getElementById('solidColorInput');
    const colorTypeRadios = document.querySelectorAll('input[name="colorType"]');
    
    // Color type toggle
    colorTypeRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            const type = e.target.value;
            const solidSection = document.getElementById('solidColorSection');
            const gradientSection = document.getElementById('gradientColorSection');
            
            // Update card active states
            document.querySelectorAll('.color-type-card').forEach(card => {
                card.classList.remove('active');
            });
            const selectedCard = e.target.closest('.color-type-card');
            if (selectedCard) {
                selectedCard.classList.add('active');
            }
            
            if (type === 'solid') {
                solidSection.style.display = 'block';
                gradientSection.style.display = 'none';
                appearanceConfig.primary_color.type = 'solid';
            } else {
                // Gradient selected
                solidSection.style.display = 'none';
                gradientSection.style.display = 'block';
                appearanceConfig.primary_color.type = 'gradient';
                
                // If no gradient colors exist, initialize with defaults
                if (gradientColors.length === 0) {
                    console.log('🔄 Initializing gradient colors');
                    addGradientColor('#1093B2', 0);
                    addGradientColor('#157A73', 100);
                }
                
                // Update gradient value to ensure preview works
                updateGradientValue();
            }
            updatePreview();
        });
    });
    
    // Initialize active state for color type cards
    const initialColorType = appearanceConfig.primary_color.type || 'solid';
    const initialRadio = document.getElementById(`colorType-${initialColorType}`);
    if (initialRadio && initialRadio.checked) {
        const initialCard = initialRadio.closest('.color-type-card');
        if (initialCard) {
            initialCard.classList.add('active');
        }
    }
    
    // Solid color picker
    if (solidColorPicker) {
        solidColorPicker.addEventListener('input', (e) => {
            const color = e.target.value;
            solidColorInput.value = color;
            appearanceConfig.primary_color.value = color;
            appearanceConfig.primary_color.contrast_text = calculateContrastText(color);
            updateContrastPreview();
            updatePreview();
        });
    }
    
    // Solid color input
    if (solidColorInput) {
        solidColorInput.addEventListener('input', (e) => {
            const color = e.target.value;
            if (isValidHexColor(color)) {
                solidColorPicker.value = color;
                appearanceConfig.primary_color.value = color;
                appearanceConfig.primary_color.contrast_text = calculateContrastText(color);
                updateContrastPreview();
                updatePreview();
            }
        });
    }
}

// Setup gradient builder
function setupGradientBuilder() {
    const addColorBtn = document.getElementById('addGradientColor');
    const gradientDirection = document.getElementById('gradientDirection');
    
    if (addColorBtn) {
        addColorBtn.addEventListener('click', () => {
            addGradientColor('#1093B2');
        });
    }
    
    if (gradientDirection) {
        gradientDirection.addEventListener('change', () => {
            updateGradientValue();
            updatePreview();
        });
    }
}

// Add gradient color stop
function addGradientColor(color = '#1093B2', position = null) {
    const gradientColorsDiv = document.getElementById('gradientColors');
    if (!gradientColorsDiv) return;
    
    const colorId = `gradient_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const colorIndex = gradientColors.length;
    
    // If position not provided, calculate it
    if (position === null) {
        if (gradientColors.length === 0) {
            position = 0;
        } else if (gradientColors.length === 1) {
            position = 100;
        } else {
            position = colorIndex * (100 / (gradientColors.length + 1));
        }
    }
    
    gradientColors.push({ id: colorId, color: color, position: position });
    
    const colorDiv = document.createElement('div');
    colorDiv.className = 'gradient-color-item';
    colorDiv.style.cssText = 'display: flex; gap: 10px; align-items: center; padding: 10px; background: #f4f4f5; border-radius: 8px;';
    colorDiv.innerHTML = `
        <input type="color" class="gradient-color-picker" value="${color}" data-id="${colorId}" style="width: 50px; height: 40px; border: 2px solid #e4e4e7; border-radius: 8px; cursor: pointer;">
        <input type="text" class="gradient-color-input" value="${color}" data-id="${colorId}" placeholder="#0891b2" style="flex: 1; padding: 8px; border: 1px solid #e4e4e7; border-radius: 8px; font-family: monospace; font-size: 14px;">
        <input type="number" class="gradient-color-position" value="${position}" min="0" max="100" data-id="${colorId}" style="width: 80px; padding: 8px; border: 1px solid #e4e4e7; border-radius: 8px; font-size: 14px;">
        <span style="color: #71717a; font-size: 14px;">%</span>
        <button type="button" class="remove-gradient-color" data-id="${colorId}" style="padding: 8px; background: #dc3545; color: white; border: none; border-radius: 8px; cursor: pointer;">
            <span class="material-icons-round" style="font-size: 18px;">delete</span>
        </button>
    `;
    
    gradientColorsDiv.appendChild(colorDiv);
    
    // Event listeners
    const colorPicker = colorDiv.querySelector('.gradient-color-picker');
    const colorInput = colorDiv.querySelector('.gradient-color-input');
    const positionInput = colorDiv.querySelector('.gradient-color-position');
    const removeBtn = colorDiv.querySelector('.remove-gradient-color');
    
    colorPicker.addEventListener('input', (e) => {
        const id = e.target.dataset.id;
        const color = e.target.value;
        updateGradientColor(id, color);
        colorInput.value = color;
    });
    
    colorInput.addEventListener('input', (e) => {
        const id = e.target.dataset.id;
        const color = e.target.value;
        if (isValidHexColor(color)) {
            updateGradientColor(id, color);
            colorPicker.value = color;
        }
    });
    
    positionInput.addEventListener('input', (e) => {
        const id = e.target.dataset.id;
        const position = parseInt(e.target.value);
        updateGradientPosition(id, position);
    });
    
    removeBtn.addEventListener('click', (e) => {
        const id = e.target.closest('.remove-gradient-color').dataset.id;
        removeGradientColor(id);
    });
    
    updateGradientValue();
    updatePreview();
}

// Update gradient color
function updateGradientColor(id, color) {
    const colorObj = gradientColors.find(c => c.id === id);
    if (colorObj) {
        colorObj.color = color;
        updateGradientValue();
        updatePreview();
    }
}

// Update gradient position
function updateGradientPosition(id, position) {
    const colorObj = gradientColors.find(c => c.id === id);
    if (colorObj) {
        colorObj.position = Math.max(0, Math.min(100, position));
        updateGradientValue();
        updatePreview();
    }
}

// Remove gradient color
function removeGradientColor(id) {
    if (gradientColors.length <= 2) {
        alert('Gradient must have at least 2 colors');
        return;
    }
    
    gradientColors = gradientColors.filter(c => c.id !== id);
    const colorDiv = document.querySelector(`[data-id="${id}"]`)?.closest('.gradient-color-item');
    if (colorDiv) {
        colorDiv.remove();
    }
    updateGradientValue();
    updatePreview();
}

// Update gradient CSS value
function updateGradientValue() {
    if (gradientColors.length < 2) return;
    
    const direction = document.getElementById('gradientDirection')?.value || 'to right';
    const sortedColors = [...gradientColors].sort((a, b) => a.position - b.position);
    const colorStops = sortedColors.map(c => `${c.color} ${c.position}%`).join(', ');
    
    appearanceConfig.primary_color.value = `linear-gradient(${direction}, ${colorStops})`;
    appearanceConfig.primary_color.contrast_text = calculateContrastTextFromGradient(sortedColors[0].color);
    updateContrastPreview();
}

// Calculate contrast text color
function calculateContrastText(hexColor) {
    // Remove # if present
    hexColor = hexColor.replace('#', '');
    
    // Convert to RGB
    const r = parseInt(hexColor.substr(0, 2), 16);
    const g = parseInt(hexColor.substr(2, 2), 16);
    const b = parseInt(hexColor.substr(4, 2), 16);
    
    // Calculate relative luminance
    const getLuminance = (val) => {
        val = val / 255;
        return val <= 0.03928 ? val / 12.92 : Math.pow((val + 0.055) / 1.055, 2.4);
    };
    
    const luminance = 0.2126 * getLuminance(r) + 0.7152 * getLuminance(g) + 0.0722 * getLuminance(b);
    
    // Return white for dark backgrounds, black for light
    return luminance < 0.5 ? '#ffffff' : '#000000';
}

// Calculate contrast from gradient (use first color)
function calculateContrastTextFromGradient(hexColor) {
    return calculateContrastText(hexColor);
}

// Update contrast preview
function updateContrastPreview() {
    const preview = document.getElementById('contrastTextPreview');
    const value = document.getElementById('contrastTextValue');
    
    if (preview && value) {
        const contrastColor = appearanceConfig.primary_color.contrast_text;
        preview.style.background = contrastColor;
        value.textContent = contrastColor;
    }
}

// Update color UI
function updateColorUI() {
    const colorType = appearanceConfig.primary_color.type;
    const colorValue = appearanceConfig.primary_color.value;
    
    console.log('🎨 Updating color UI:', { colorType, colorValue });
    
    // Get sections and radio buttons
    const solidSection = document.getElementById('solidColorSection');
    const gradientSection = document.getElementById('gradientColorSection');
    const solidRadio = document.querySelector('input[name="colorType"][value="solid"]');
    const gradientRadio = document.querySelector('input[name="colorType"][value="gradient"]');
    
    // First, uncheck all radio buttons and remove active class from cards
    if (solidRadio) solidRadio.checked = false;
    if (gradientRadio) gradientRadio.checked = false;
    document.querySelectorAll('.color-type-card').forEach(card => {
        card.classList.remove('active');
    });
    
    // Then set the correct radio button based on saved type
    if (colorType === 'gradient') {
        // User has gradient saved - select gradient radio
        if (gradientRadio) {
            gradientRadio.checked = true;
            console.log('✅ Gradient radio button selected');
        }
        
        // Set active state on gradient card
        const gradientCard = document.querySelector('.color-type-card[data-color-type="gradient"]');
        if (gradientCard) {
            gradientCard.classList.add('active');
        }
        
        // Show gradient section, hide solid section
        if (solidSection) solidSection.style.display = 'none';
        if (gradientSection) gradientSection.style.display = 'block';
        
        // Parse and load gradient colors
        console.log('🔄 Parsing gradient:', colorValue);
        parseGradientValue(colorValue);
    } else {
        // User has solid color saved - select solid radio
        if (solidRadio) {
            solidRadio.checked = true;
            console.log('✅ Solid radio button selected');
        }
        
        // Set active state on solid card
        const solidCard = document.querySelector('.color-type-card[data-color-type="solid"]');
        if (solidCard) {
            solidCard.classList.add('active');
        }
        
        // Show solid section, hide gradient section
        if (solidSection) solidSection.style.display = 'block';
        if (gradientSection) gradientSection.style.display = 'none';
        
        // Set solid color values
        const solidPicker = document.getElementById('solidColorPicker');
        const solidInput = document.getElementById('solidColorInput');
        if (solidPicker) {
            solidPicker.value = colorValue;
            console.log('✅ Solid color picker set to:', colorValue);
        }
        if (solidInput) {
            solidInput.value = colorValue;
            console.log('✅ Solid color input set to:', colorValue);
        }
    }
    
    updateContrastPreview();
}

// Setup avatar selection
function setupAvatarSelection() {
    const showPresetsBtn = document.getElementById('showPresetsBtn');
    const showUploadBtn = document.getElementById('showUploadBtn');
    const presetSection = document.getElementById('presetAvatarsSection');
    const uploadSection = document.getElementById('uploadAvatarSection');
    const avatarUpload = document.getElementById('avatarUpload');
    const removeAvatarBtn = document.getElementById('removeAvatarBtn');
    
    // Tab toggle
    if (showPresetsBtn) {
        showPresetsBtn.addEventListener('click', () => {
            showPresetsBtn.classList.add('active');
            showPresetsBtn.style.background = '#0891b2';
            showPresetsBtn.style.color = 'white';
            showUploadBtn.classList.remove('active');
            showUploadBtn.style.background = '#f4f4f5';
            showUploadBtn.style.color = '#52525b';
            presetSection.style.display = 'block';
            uploadSection.style.display = 'none';
        });
    }
    
    if (showUploadBtn) {
        showUploadBtn.addEventListener('click', () => {
            showUploadBtn.classList.add('active');
            showUploadBtn.style.background = '#0891b2';
            showUploadBtn.style.color = 'white';
            showPresetsBtn.classList.remove('active');
            showPresetsBtn.style.background = '#f4f4f5';
            showPresetsBtn.style.color = '#52525b';
            presetSection.style.display = 'none';
            uploadSection.style.display = 'block';
        });
    }
    
    // Preset selection - use event delegation for better reliability
    const presetGrid = document.getElementById('presetAvatarsGrid');
    if (presetGrid) {
        // Remove any existing listeners
        const newPresetGrid = presetGrid.cloneNode(true);
        presetGrid.parentNode.replaceChild(newPresetGrid, presetGrid);
        
        // Add click listener with event delegation
        newPresetGrid.addEventListener('click', (e) => {
            // Check if click is on preset item or its children
            const presetItem = e.target.closest('.preset-avatar-item');
            if (!presetItem) return;
            
            e.preventDefault();
            e.stopPropagation();
            
            const presetId = presetItem.dataset.preset;
            const presetName = presetItem.dataset.name;
            
            console.log('🎯 Preset avatar clicked:', { presetId, presetName });
            
            appearanceConfig.avatar = {
                type: 'preset',
                value: presetId,
                name: presetName,
                fallback: 'ui-avatars'
            };
            
            // Update selection - highlight the avatar circle
            document.querySelectorAll('.preset-avatar-item').forEach(item => {
                const avatarCircle = item.querySelector('div');
                if (avatarCircle) {
                    avatarCircle.style.borderColor = '#e4e4e7';
                    avatarCircle.style.borderWidth = '2px';
                    avatarCircle.style.boxShadow = 'none';
                }
            });
            
            const selectedCircle = presetItem.querySelector('div');
            if (selectedCircle) {
                selectedCircle.style.borderColor = '#0891b2';
                selectedCircle.style.borderWidth = '3px';
                selectedCircle.style.boxShadow = '0 0 0 2px rgba(8, 145, 178, 0.2)';
            }
            
            updateAvatarUI();
            updatePreview();
        });
    }
    
    // Upload (UI ready, backend later)
    if (avatarUpload) {
        avatarUpload.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const fileName = document.getElementById('avatarFileName');
                if (fileName) {
                    fileName.textContent = file.name;
                }
                if (removeAvatarBtn) {
                    removeAvatarBtn.style.display = 'inline-block';
                }
                // Preview will be implemented in Phase 4
            }
        });
    }
    
        if (removeAvatarBtn) {
        removeAvatarBtn.addEventListener('click', () => {
            appearanceConfig.avatar = {
                type: 'preset',
                value: 'avatar_1',
                name: 'cort',
                fallback: 'ui-avatars'
            };
            if (avatarUpload) avatarUpload.value = '';
            const fileName = document.getElementById('avatarFileName');
            if (fileName) fileName.textContent = 'No file selected';
            removeAvatarBtn.style.display = 'none';
            updateAvatarUI();
            updatePreview();
        });
    }
}

// Update avatar UI
function updateAvatarUI() {
    const currentAvatarPreview = document.getElementById('currentAvatarPreview');
    if (currentAvatarPreview && appearanceConfig.avatar) {
        if (appearanceConfig.avatar.type === 'preset') {
            const avatarId = appearanceConfig.avatar.value;
            const avatarName = appearanceConfig.avatar.name || avatarId.replace('avatar_', '');
            currentAvatarPreview.innerHTML = `<img src="/static/img/avatar/${avatarId}.png" alt="${avatarName}" style="width: 100%; height: 100%; border-radius: 50%; object-fit: cover;">`;
            
            // Also update selection in grid
            document.querySelectorAll('.preset-avatar-item').forEach(item => {
                const avatarCircle = item.querySelector('div');
                if (avatarCircle) {
                    if (item.dataset.preset === avatarId) {
                        avatarCircle.style.borderColor = '#0891b2';
                        avatarCircle.style.borderWidth = '3px';
                        avatarCircle.style.boxShadow = '0 0 0 2px rgba(8, 145, 178, 0.2)';
                    } else {
                        avatarCircle.style.borderColor = '#e4e4e7';
                        avatarCircle.style.borderWidth = '2px';
                        avatarCircle.style.boxShadow = 'none';
                    }
                }
            });
        } else if (appearanceConfig.avatar.type === 'upload') {
            // Will show uploaded avatar in Phase 4
            currentAvatarPreview.innerHTML = `<img src="/${appearanceConfig.avatar.value}" alt="Avatar" style="width: 100%; height: 100%; border-radius: 50%; object-fit: cover;">`;
        } else {
            // Default fallback
            currentAvatarPreview.innerHTML = '<span class="material-icons-round" style="font-size: 40px; color: #71717a;">face</span>';
        }
    }
}

// Setup suggested messages
function setupSuggestedMessages() {
    const addMessageBtn = document.getElementById('addMessageBtn');
    const messagesList = document.getElementById('suggestedMessagesList');
    
    if (addMessageBtn) {
        addMessageBtn.addEventListener('click', () => {
            if (appearanceConfig.suggested_messages.length >= 5) {
                alert('Maximum 5 suggested messages allowed');
                return;
            }
            addSuggestedMessage('', true);
        });
    }
    
    // Initialize drag and drop
    if (messagesList) {
        makeSortable(messagesList);
    }
}

// Add suggested message
function addSuggestedMessage(text = '', isNew = false) {
    messageCounter++;
    const messageId = isNew ? `msg_${Date.now()}` : (text.id || `msg_${messageCounter}`);
    const messageText = isNew ? text : (text.text || text);
    const order = isNew ? appearanceConfig.suggested_messages.length + 1 : (text.order || appearanceConfig.suggested_messages.length + 1);
    
    if (isNew) {
        appearanceConfig.suggested_messages.push({
            id: messageId,
            text: messageText,
            order: order
        });
    }
    
    updateSuggestedMessagesUI();
    updatePreview();
}

// Update suggested messages UI
function updateSuggestedMessagesUI() {
    const messagesList = document.getElementById('suggestedMessagesList');
    if (!messagesList) {
        console.warn('⚠️ suggestedMessagesList element not found');
        return;
    }
    
    console.log('🔄 Updating suggested messages UI:', appearanceConfig.suggested_messages);
    
    if (!appearanceConfig.suggested_messages || appearanceConfig.suggested_messages.length === 0) {
        console.warn('⚠️ No suggested messages to display');
        messagesList.innerHTML = '<p style="color: #71717a; font-size: 14px; padding: 10px;">No suggested messages. Click "Add Message" to add one.</p>';
        return;
    }
    
    // Sort by order
    const sortedMessages = [...appearanceConfig.suggested_messages].sort((a, b) => a.order - b.order);
    
    messagesList.innerHTML = '';
    
    sortedMessages.forEach((msg, index) => {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'suggested-message-item';
        messageDiv.dataset.id = msg.id;
        messageDiv.style.cssText = 'display: flex; gap: 10px; align-items: center; padding: 12px; background: #f4f4f5; border-radius: 8px; cursor: move;';
        messageDiv.innerHTML = `
            <span class="material-icons-round drag-handle" style="color: #71717a; cursor: grab; user-select: none;">drag_handle</span>
            <input type="text" class="message-text-input" value="${msg.text}" data-id="${msg.id}" placeholder="Enter message..." maxlength="60" style="flex: 1; padding: 8px; border: 1px solid #e4e4e7; border-radius: 6px; font-size: 14px;">
            <button type="button" class="remove-message-btn" data-id="${msg.id}" style="padding: 8px; background: #dc3545; color: white; border: none; border-radius: 6px; cursor: pointer;">
                <span class="material-icons-round" style="font-size: 18px;">delete</span>
            </button>
        `;
        
        messagesList.appendChild(messageDiv);
        
        // Event listeners
        const textInput = messageDiv.querySelector('.message-text-input');
        const removeBtn = messageDiv.querySelector('.remove-message-btn');
        
        textInput.addEventListener('input', (e) => {
            const id = e.target.dataset.id;
            const message = appearanceConfig.suggested_messages.find(m => m.id === id);
            if (message) {
                message.text = e.target.value;
                updatePreview();
            }
        });
        
        removeBtn.addEventListener('click', (e) => {
            const id = e.target.closest('.remove-message-btn').dataset.id;
            if (appearanceConfig.suggested_messages.length <= 1) {
                alert('At least one message is required');
                return;
            }
            appearanceConfig.suggested_messages = appearanceConfig.suggested_messages.filter(m => m.id !== id);
            updateSuggestedMessagesUI();
            updatePreview();
        });
    });
    
    // Re-initialize drag and drop
    makeSortable(messagesList);
}

// Make list sortable (drag and drop)
function makeSortable(container) {
    let draggedElement = null;
    
    container.querySelectorAll('.suggested-message-item').forEach(item => {
        item.draggable = true;
        
        item.addEventListener('dragstart', (e) => {
            draggedElement = item;
            item.style.opacity = '0.5';
            e.dataTransfer.effectAllowed = 'move';
        });
        
        item.addEventListener('dragend', () => {
            item.style.opacity = '1';
            draggedElement = null;
        });
        
        item.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
            
            const afterElement = getDragAfterElement(container, e.clientY);
            if (afterElement == null) {
                container.appendChild(draggedElement);
            } else {
                container.insertBefore(draggedElement, afterElement);
            }
        });
        
        item.addEventListener('drop', (e) => {
            e.preventDefault();
            updateMessageOrder();
        });
    });
}

// Get element after drag position
function getDragAfterElement(container, y) {
    const draggableElements = [...container.querySelectorAll('.suggested-message-item:not(.dragging)')];
    
    return draggableElements.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = y - box.top - box.height / 2;
        
        if (offset < 0 && offset > closest.offset) {
            return { offset: offset, element: child };
        } else {
            return closest;
        }
    }, { offset: Number.NEGATIVE_INFINITY }).element;
}

// Update message order after drag
function updateMessageOrder() {
    const messagesList = document.getElementById('suggestedMessagesList');
    if (!messagesList) return;
    
    const items = messagesList.querySelectorAll('.suggested-message-item');
    items.forEach((item, index) => {
        const id = item.dataset.id;
        const message = appearanceConfig.suggested_messages.find(m => m.id === id);
        if (message) {
            message.order = index + 1;
        }
    });
    
    updatePreview();
}

// Setup description input
function setupDescriptionInput() {
    const descriptionInput = document.getElementById('chatbotDescription');
    if (descriptionInput) {
        descriptionInput.addEventListener('input', (e) => {
            appearanceConfig.description = e.target.value;
            updatePreview();
        });
    }
}

// Setup save button
function setupSaveButton() {
    const saveBtn = document.getElementById('saveAppearanceBtn');
    if (saveBtn) {
        saveBtn.addEventListener('click', saveAppearanceConfig);
    }
}

// Save appearance configuration
async function saveAppearanceConfig() {
    const successAlert = document.getElementById('appearanceSuccess');
    const errorAlert = document.getElementById('appearanceError');
    
    // Hide previous alerts
    if (successAlert) successAlert.style.display = 'none';
    if (errorAlert) errorAlert.style.display = 'none';
    
    try {
        // Get current config
        const response = await fetch('/api/user/chatbot-config');
        const data = await response.json();
        const currentConfig = data.config || data;
        
        console.log('💾 Saving appearance config:', {
            primary_color: appearanceConfig.primary_color,
            primary_color_type: appearanceConfig.primary_color.type,
            primary_color_value: appearanceConfig.primary_color.value ? (appearanceConfig.primary_color.value.substring(0, 50) + '...') : 'null'
        });
        
        // Update with appearance settings
        currentConfig.short_info = appearanceConfig.description;
        currentConfig.primary_color = appearanceConfig.primary_color; // This should be an object with type and value
        currentConfig.avatar = appearanceConfig.avatar;
        currentConfig.suggested_messages = appearanceConfig.suggested_messages;
        
        console.log('📤 Sending to API:', {
            primary_color: currentConfig.primary_color,
            primary_color_type: typeof currentConfig.primary_color
        });
        
        // Save
        const saveResponse = await fetch('/api/user/chatbot-config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(currentConfig)
        });
        
        const result = await saveResponse.json();
        
        if (saveResponse.ok) {
            const message = 'Appearance settings saved successfully!';
            if (successAlert) {
                successAlert.textContent = message;
                successAlert.style.display = 'block';
            }
            // Show toast notification
            if (typeof showSuccessNotification === 'function') {
                showSuccessNotification(message, 5000);
            }
        } else {
            throw new Error(result.error || 'Failed to save appearance settings');
        }
    } catch (error) {
        console.error('Failed to save appearance config:', error);
        const errorMessage = 'Error: ' + error.message;
        if (errorAlert) {
            errorAlert.textContent = errorMessage;
            errorAlert.style.display = 'block';
        }
        // Show toast notification
        if (typeof showErrorNotification === 'function') {
            showErrorNotification(errorMessage, 6000);
        }
    }
}

// Update preview panel
function updatePreview() {
    updatePreviewDescription();
    updatePreviewColor();
    updatePreviewAvatar();
    updatePreviewMessages();
}

// Update preview description
function updatePreviewDescription() {
    const descriptionEl = document.getElementById('previewBotDescription');
    if (descriptionEl) {
        descriptionEl.textContent = appearanceConfig.description || 'Your friendly assistant';
    }
}

// Update preview color
function updatePreviewColor() {
    const primaryColor = appearanceConfig.primary_color.value;
    const contrastText = appearanceConfig.primary_color.contrast_text;
    
    // Trigger button
    const triggerBtn = document.getElementById('previewTriggerButton');
    if (triggerBtn) {
        triggerBtn.style.background = primaryColor;
    }
    
    // Chatbox header
    const header = document.getElementById('previewChatboxHeader');
    if (header) {
        header.style.background = primaryColor;
        header.style.color = contrastText;
    }
    
    // Send button
    const sendBtn = document.getElementById('previewSendButton');
    if (sendBtn) {
        sendBtn.style.background = primaryColor;
    }
}

// Update preview avatar
function updatePreviewAvatar() {
    const triggerAvatar = document.getElementById('previewTriggerAvatar');
    const headerAvatar = document.getElementById('previewHeaderAvatar');
    const headerIcon = document.getElementById('previewHeaderIcon');
    
    if (appearanceConfig.avatar && appearanceConfig.avatar.type === 'preset') {
        const avatarId = appearanceConfig.avatar.value;
        const avatarPath = `/static/img/avatar/${avatarId}.png`;
        
        if (triggerAvatar) {
            triggerAvatar.src = avatarPath;
            triggerAvatar.style.display = 'block';
        }
        
        if (headerAvatar) {
            headerAvatar.src = avatarPath;
            headerAvatar.style.display = 'block';
            if (headerIcon) headerIcon.style.display = 'none';
        }
    } else {
        // Show icon fallback for header only (trigger always shows avatar)
        if (triggerAvatar) {
            // Default avatar if none selected
            triggerAvatar.src = '/static/img/avatar/avatar_1.png';
            triggerAvatar.style.display = 'block';
        }
        if (headerAvatar) headerAvatar.style.display = 'none';
        if (headerIcon) headerIcon.style.display = 'block';
    }
}

// Update preview messages
function updatePreviewMessages() {
    const previewMessages = document.getElementById('previewSuggestedMessages');
    if (!previewMessages) return;
    
    previewMessages.innerHTML = '';
    
    const sortedMessages = [...appearanceConfig.suggested_messages]
        .sort((a, b) => a.order - b.order)
        .slice(0, 5);
    
    sortedMessages.forEach(msg => {
        const button = document.createElement('button');
        button.textContent = msg.text || 'Message';
        button.style.cssText = 'padding: 8px 16px; background: white; border: 1px solid #e4e4e7; border-radius: 20px; font-size: 14px; color: #52525b; white-space: nowrap; cursor: default;';
        previewMessages.appendChild(button);
    });
}

// Parse gradient value and populate gradient builder
function parseGradientValue(gradientValue) {
    console.log('🔄 Parsing gradient value:', gradientValue);
    
    if (!gradientValue || !gradientValue.includes('linear-gradient')) {
        console.log('⚠️ Invalid gradient value, using defaults');
        // Default gradient if invalid
        if (gradientColors.length === 0) {
            addGradientColor('#0891b2', 0);
            addGradientColor('#764ba2', 100);
        }
        return;
    }
    
    // Clear existing gradient colors
    gradientColors = [];
    const gradientColorsDiv = document.getElementById('gradientColors');
    if (gradientColorsDiv) {
        gradientColorsDiv.innerHTML = '';
        console.log('✅ Cleared existing gradient colors');
    }
    
    // Extract direction
    const directionMatch = gradientValue.match(/linear-gradient\(([^,]+),/);
    const direction = directionMatch ? directionMatch[1].trim() : 'to right';
    const directionSelect = document.getElementById('gradientDirection');
    if (directionSelect) {
        directionSelect.value = direction;
        console.log('✅ Gradient direction set to:', direction);
    }
    
    // Extract color stops: "linear-gradient(to right, #0891b2 0%, #764ba2 50%, #f093fb 100%)"
    const colorStopsMatch = gradientValue.match(/linear-gradient\([^,]+,\s*(.+)\)/);
    if (colorStopsMatch) {
        const colorStops = colorStopsMatch[1];
        console.log('📋 Color stops string:', colorStops);
        
        // Split by comma, but be careful with rgba/hsla colors
        // Use a more sophisticated split that handles rgba/hsla
        const stops = [];
        let currentStop = '';
        let parenDepth = 0;
        
        for (let i = 0; i < colorStops.length; i++) {
            const char = colorStops[i];
            if (char === '(') parenDepth++;
            if (char === ')') parenDepth--;
            if (char === ',' && parenDepth === 0) {
                stops.push(currentStop.trim());
                currentStop = '';
            } else {
                currentStop += char;
            }
        }
        if (currentStop.trim()) {
            stops.push(currentStop.trim());
        }
        
        console.log('📋 Parsed stops:', stops);
        
        stops.forEach((stop, index) => {
            // Match color and position: "#0891b2 0%" or "rgba(8, 145, 178, 1) 50%"
            const match = stop.match(/^(.+?)\s+(\d+)%$/);
            if (match) {
                const color = match[1].trim();
                const position = parseInt(match[2]);
                console.log(`  ✓ Adding color stop: ${color} at ${position}%`);
                addGradientColor(color, position);
            } else {
                // No position specified, calculate it
                const position = stops.length > 1 ? (index / (stops.length - 1)) * 100 : (index * 50);
                console.log(`  ✓ Adding color stop: ${stop.trim()} at ${position}% (calculated)`);
                addGradientColor(stop.trim(), position);
            }
        });
    } else {
        console.log('⚠️ Could not parse color stops, trying fallback');
        // Fallback: try to extract colors without positions
        const colorRegex = /#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})|rgba?\([^)]+\)|hsla?\([^)]+\)/gi;
        const colors = gradientValue.match(colorRegex);
        if (colors && colors.length >= 2) {
            console.log('📋 Found colors via regex:', colors);
            colors.forEach((color, index) => {
                const position = (index / (colors.length - 1)) * 100;
                addGradientColor(color, position);
            });
        } else {
            console.log('⚠️ No colors found, using defaults');
            // Default gradient
            addGradientColor('#0891b2', 0);
            addGradientColor('#764ba2', 100);
        }
    }
    
    console.log('✅ Gradient parsing complete. Colors:', gradientColors.length);
}

// Validate hex color
function isValidHexColor(color) {
    return /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/.test(color);
}

// Initialize on tab switch (called from switchTab function)
// Also initialize on DOMContentLoaded if tab is already active
document.addEventListener('DOMContentLoaded', () => {
    const appearanceTab = document.getElementById('appearance-tab');
    if (appearanceTab && appearanceTab.classList.contains('active')) {
        initializeAppearance();
    }
});

