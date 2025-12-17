/**
 * User Info Form Module
 * Handles user information collection form
 * Matches chatbot design with dynamic colors
 */
class UserInfoForm {
    constructor(options = {}) {
        this.conversationId = options.conversationId || null;
        this.apiKey = options.apiKey || null;
        this.apiBaseUrl = options.apiBaseUrl || window.location.origin;
        this.primaryColor = options.primaryColor || '#0891b2';
        this.contrastColor = options.contrastColor || '#ffffff';
        this.onSubmit = options.onSubmit || null;
        this.onSkip = options.onSkip || null;
        this.container = null;
        this.formElement = null;
    }

    create() {
        const container = document.createElement('div');
        container.id = 'user-info-form-container';
        container.style.cssText = `
            padding: 20px;
            background: white;
            border-radius: 20px;
            margin: 16px;
            animation: fadeIn 0.3s ease-out;
        `;

        const form = document.createElement('form');
        form.id = 'user-info-form';
        form.style.cssText = `
            display: flex;
            flex-direction: column;
        `;

        const title = document.createElement('h3');
        title.textContent = 'Tell us about yourself';
        title.style.cssText = `
            font-size: 18px;
            font-weight: 600;
            color: #18181b;
            margin: 0 0 8px 0;
        `;

        const subtitle = document.createElement('p');
        subtitle.textContent = 'This helps us personalize your experience';
        subtitle.style.cssText = `
            font-size: 14px;
            color: #71717a;
            margin: 0 0 16px 0;
        `;

        const nameGroup = this.createInputGroup('name', 'Name', true);
        const emailGroup = this.createInputGroup('email', 'Email (optional)', false);
        const phoneGroup = this.createInputGroup('phone', 'Phone (optional)', false);

        const buttonGroup = document.createElement('div');
        buttonGroup.style.cssText = `
            display: flex;
            gap: 12px;
            margin-top: 8px;
        `;

        const skipBtn = this.createButton('Skip', 'skip', false);
        const confirmBtn = this.createButton('Confirm', 'confirm', true);

        buttonGroup.appendChild(skipBtn);
        buttonGroup.appendChild(confirmBtn);

        form.appendChild(title);
        form.appendChild(subtitle);
        form.appendChild(nameGroup);
        form.appendChild(emailGroup);
        form.appendChild(phoneGroup);
        form.appendChild(buttonGroup);

        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSubmit();
        });

        skipBtn.addEventListener('click', (e) => {
            e.preventDefault();
            this.handleSkip();
        });

        container.appendChild(form);
        this.container = container;
        this.formElement = form;
        return container;
    }

    createInputGroup(name, label, required) {
        const group = document.createElement('div');
        group.style.cssText = `
            display: flex;
            flex-direction: column;
            gap: 8px;
        `;

        const labelEl = document.createElement('label');
        labelEl.textContent = label;
        labelEl.setAttribute('for', `user-info-${name}`);
        labelEl.style.cssText = `
            font-size: 14px;
            font-weight: 500;
            color: #27272a;
        `;

        const input = document.createElement('input');
        input.type = name === 'email' ? 'email' : 'text';
        input.id = `user-info-${name}`;
        input.name = name;
        input.required = required;
        input.style.cssText = `
            padding: 5px;
            border: 1.5px solid #e4e4e7;
            border-radius: 6px;
            font-size: 16px;
            font-family: inherit;
            color: #18181b;
            background: white;
            transition: border-color 0.2s;
            outline: none;
        `;

        input.addEventListener('focus', () => {
            input.style.borderColor = this.primaryColor;
        });

        input.addEventListener('blur', () => {
            input.style.borderColor = '#e4e4e7';
        });

        group.appendChild(labelEl);
        group.appendChild(input);
        return group;
    }

    createButton(text, type, isPrimary) {
        const button = document.createElement('button');
        button.type = type === 'skip' ? 'button' : 'submit';
        button.textContent = text;
        
        if (isPrimary) {
            button.style.cssText = `
                flex: 1;
                background: ${this.primaryColor};
                color: ${this.contrastColor};
                border: none;
                padding: 5px;
                border-radius: 6px;
                font-size: 16px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
            `;
            button.addEventListener('mouseenter', () => {
                button.style.transform = 'translateY(-1px)';
                button.style.opacity = '0.9';
            });
            button.addEventListener('mouseleave', () => {
                button.style.transform = 'translateY(0)';
                button.style.opacity = '1';
            });
        } else {
            button.style.cssText = `
                flex: 1;
                background: white;
                color: #52525b;
                border: 1.5px solid #e4e4e7;
                padding: 5px;
                border-radius: 6px;
                font-size: 16px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s;
            `;
            button.addEventListener('mouseenter', () => {
                button.style.borderColor = '#d4d4d8';
                button.style.backgroundColor = '#f4f4f5';
            });
            button.addEventListener('mouseleave', () => {
                button.style.borderColor = '#e4e4e7';
                button.style.backgroundColor = 'white';
            });
        }

        return button;
    }

    async handleSubmit() {
        if (!this.conversationId) {
            console.error('No conversation ID');
            return;
        }

        const nameInput = document.getElementById('user-info-name');
        const emailInput = document.getElementById('user-info-email');
        const phoneInput = document.getElementById('user-info-phone');

        let name = nameInput.value.trim();
        const email = emailInput.value.trim();
        const phone = phoneInput.value.trim();

        if (!name) {
            alert('Name is required');
            return;
        }

        // Capitalize name: first letter uppercase, rest lowercase
        if (name.length > 0) {
            name = name.charAt(0).toUpperCase() + name.slice(1).toLowerCase();
        }

        const confirmBtn = this.formElement.querySelector('button[type="submit"]');
        const originalText = confirmBtn.textContent;
        confirmBtn.disabled = true;
        confirmBtn.textContent = 'Saving...';

        try {
            const url = `${this.apiBaseUrl}/conversations/${this.conversationId}/user-info`;
            
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': this.apiKey || ''
                },
                body: JSON.stringify({
                    name: name,
                    email: email || null,
                    phone: phone || null
                })
            });


            if (!response.ok) {
                let errorMessage = 'Failed to save user info';
                const contentType = response.headers.get('content-type');
                
                if (contentType && contentType.includes('application/json')) {
                    try {
                        const error = await response.json();
                        errorMessage = error.error || errorMessage;
                    } catch (e) {
                        errorMessage = `Server error (${response.status})`;
                    }
                } else {
                    await response.text();
                    errorMessage = `Server error (${response.status}): ${response.statusText}`;
                }
                throw new Error(errorMessage);
            }

            this.hide();
            if (this.onSubmit) {
                this.onSubmit({ name, email, phone });
            }
        } catch (error) {
            alert('Failed to save user info. Please try again.');
            confirmBtn.disabled = false;
            confirmBtn.textContent = originalText;
        }
    }

    handleSkip() {
        this.hide();
        if (this.onSkip) {
            this.onSkip();
        }
    }

    show(parentElement) {
        if (!this.container) {
            this.create();
        }
        if (parentElement) {
            parentElement.appendChild(this.container);
        }
    }

    hide() {
        if (this.container && this.container.parentNode) {
            this.container.parentNode.removeChild(this.container);
        }
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UserInfoForm;
}

