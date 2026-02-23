let conversationHistory = [];
let userProfile = {
    name: null,
    age: null,
    gender: null,
    height: null,
    weight: null,
    fitness_goals: null,
    activity_level: null
};

// Health onboarding: ask_fixed | ask_goal | follow_up | complete (null = loading)
let onboardingPhase = null;

document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const generatePlanBtn = document.getElementById('generate-plan-btn');

    const username = sessionStorage.getItem('username');
    if (!username) {
        window.location.href = '/';
        return;
    }

    // Load health data (age, gender, height, weight, fitness_goal) from HealthData; profile table has only user_id
    fetch('/api/profile/health?timestamp=health_profile')
        .then(r => r.ok ? r.json() : null)
        .then(data => {
            if (data && data.health_data) {
                const h = data.health_data;
                userProfile.age = h.age != null ? h.age : userProfile.age;
                userProfile.gender = h.gender || userProfile.gender;
                userProfile.height = h.height != null ? h.height : userProfile.height;
                userProfile.weight = h.weight != null ? h.weight : userProfile.weight;
                userProfile.fitness_goals = h.fitness_goal ? [h.fitness_goal] : userProfile.fitness_goals;
            }
        })
        .catch(() => {})
        .finally(() => {
            // Start LLM health onboarding: fixed stats from HealthData → ask goal → follow-up Q&A
            fetch('/api/chat/health-onboarding', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: '' })
            })
                .then(r => r.json())
                .then(data => {
                    if (data.success && data.response) {
                        onboardingPhase = data.phase || 'ask_fixed';
                        addMessage('ai', data.response);
                    } else {
                        addMessage('ai', data.error || 'Something went wrong. You can still ask me anything.');
                        onboardingPhase = 'complete';
                    }
                })
                .catch(() => {
                    addMessage('ai', 'Unable to load. You can still type and ask questions.');
                    onboardingPhase = 'complete';
                });
        });

    // Send message on button click
    sendBtn.addEventListener('click', handleSend);

    // Send message on Enter key
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !sendBtn.disabled) {
            handleSend();
        }
    });

    // Generate plan button
    generatePlanBtn.addEventListener('click', async function() {
        if (onboardingPhase === 'ask_fixed' || onboardingPhase === 'ask_goal' || onboardingPhase === 'follow_up') {
            addMessage('ai', 'Please complete the health setup questions above first, then I can generate your plan.');
            return;
        }
        const hasProfile = userProfile.age != null || userProfile.height != null || userProfile.weight != null ||
            (userProfile.fitness_goals && userProfile.fitness_goals.length);
        if (!hasProfile) {
            addMessage('ai', 'Share your fitness goal in the chat above first.');
            return;
        }
        generatePlanBtn.disabled = true;
        generatePlanBtn.textContent = 'Generating...';
        try {
            const goals = userProfile.fitness_goals && userProfile.fitness_goals.length
                ? userProfile.fitness_goals.join(', ') : 'general fitness';
            const prompt = `Create a personalized fitness plan. Profile: Age ${userProfile.age || 'not set'}, Gender ${userProfile.gender || 'not set'}, Height ${userProfile.height || 'not set'}, Weight ${userProfile.weight || 'not set'}. Fitness goal: ${goals}. Provide workout routines, nutrition advice, and goals.`;
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: prompt, profile: userProfile })
            });
            const data = await response.json();
            if (response.ok) addMessage('ai', data.response);
            else addMessage('ai', data.error || 'Sorry, I encountered an error. Please try again.');
        } catch (err) {
            console.error(err);
            addMessage('ai', 'Sorry, I encountered an error. Please try again.');
        } finally {
            generatePlanBtn.disabled = false;
            generatePlanBtn.textContent = 'Generate Plan';
        }
    });

    async function handleSend() {
        const message = userInput.value.trim();
        if (!message || sendBtn.disabled) return;

        addMessage('user', message);
        userInput.value = '';
        sendBtn.disabled = true;

        if (onboardingPhase === 'ask_fixed' || onboardingPhase === 'ask_goal' || onboardingPhase === 'follow_up') {
            try {
                const response = await fetch('/api/chat/health-onboarding', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });
                const data = await response.json();
                if (response.ok && data.success) {
                    onboardingPhase = data.phase || 'complete';
                    addMessage('ai', data.response);
                } else {
                    addMessage('ai', data.error || 'Something went wrong. Please try again.');
                }
            } catch (err) {
                console.error(err);
                addMessage('ai', 'Network error. Please try again.');
            } finally {
                sendBtn.disabled = false;
                userInput.focus();
            }
            return;
        }

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message, profile: userProfile })
            });
            const data = await response.json();
            if (response.ok) addMessage('ai', data.response);
            else addMessage('ai', data.error || 'Sorry, I encountered an error. Please try again.');
        } catch (err) {
            console.error(err);
            addMessage('ai', 'Network error. Please check your connection and try again.');
        } finally {
            sendBtn.disabled = false;
            userInput.focus();
        }
    }

    function addMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';

        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        bubble.textContent = text;

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(bubble);

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});

