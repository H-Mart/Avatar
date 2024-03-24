class InstructionStateMachine {
    constructor() {
        this.socket = io.connect('http://' + document.domain + ':' + location.port);
        this.currentState = 'Configuration';
        this.instructions = [];
        this.countdownTime = 5;
        this.recordingTime = 15;
        this.numRounds = 5;
        this.currentInstructionIndex = 0;
        this.currentRound = 0;
        this.session = new Date().getTime();
        this.bindElements();
        this.bindEvents();
        this.showConfigScreen();
    }

    bindElements() {
        this.configScreen = document.getElementById('configScreen');
        this.appScreen = document.getElementById('app');
        this.startButton = document.getElementById('startButton');
        this.countdownDisplay = document.getElementById('countdown');
        this.instructionDisplay = document.getElementById('instruction');
        this.addInstructionBtn = document.getElementById('addInstruction');
        this.startConfigBtn = document.getElementById('startConfig');
        this.instructionsContainer = document.getElementById('instructionsContainer');
    }

    bindEvents() {
        this.addInstructionBtn.addEventListener('click', () => this.addInstructionInput());
        this.startConfigBtn.addEventListener('click', () => this.startFromConfig());
        this.startButton.addEventListener('click', () => {
            if (this.currentState === 'Idle') {
                this.transition('Countdown');
            }
        });
    }

    addInstructionInput(instructionText = 'Instruction Text', instructionLabel = 'Instruction Label') {
        const instructionDiv = document.createElement('div');
        instructionDiv.className = 'instructionInput';

        const instructionInput = document.createElement('input');
        instructionInput.type = 'text';
        instructionInput.placeholder = 'Instruction Text';
        instructionInput.value = instructionText;

        const labelInput = document.createElement('input');
        labelInput.type = 'text';
        labelInput.placeholder = 'Instruction Label';
        labelInput.value = instructionLabel;


        instructionDiv.appendChild(instructionInput);
        instructionDiv.appendChild(labelInput);
        this.instructionsContainer.insertBefore(instructionDiv, this.addInstructionBtn);
    }

    addDefaultInstructions() {
        this.addInstructionInput('Drone go left', 'left');
        this.addInstructionInput('Drone go right', 'right');
        this.addInstructionInput('Drone go takeoff', 'takeoff');
        this.addInstructionInput('Drone go land', 'land');
        this.addInstructionInput('Drone go forward', 'forward');
        this.addInstructionInput('Drone go backward', 'backward');
    }

    startFromConfig() {
        console.log('Starting from configuration');
        const instructionElements = this.instructionsContainer.getElementsByClassName('instructionInput');
        this.instructions = Array.from(instructionElements).map(elem => ({
            text: elem.children[0].value,
            label: elem.children[1].value
        })).filter(instr => instr.text && instr.label);

        this.countdownTime = document.getElementById('countdownLength').value || 5;
        this.recordingTime = document.getElementById('recordingTime').value || 15;
        this.numRounds = document.getElementById('numberOfRounds').value || 5;

        if (this.instructions.length > 0) {
            this.configScreen.style.display = 'none';
            this.appScreen.style.display = 'block';
            this.startButton.style.display = 'block';
            this.currentState = 'Idle';
        } else {
            alert("Please add at least one instruction with its label.");
        }
    }

    showConfigScreen() {
        this.configScreen.style.display = 'flex';
        this.appScreen.style.display = 'none';
        this.startButton.style.display = 'none';
        this.currentState = 'Configuration';
        // Reset instructions container for fresh input
        this.instructionsContainer.innerHTML = '<button id="addInstruction">Add Instruction</button>';
        this.bindElements()
        this.bindEvents(); // Re-bind events as the addInstructionBtn element was re-created
        this.addDefaultInstructions();
    }

    transition(newState) {
        switch (newState) {
            case 'Configuration':
                this.showConfigScreen();
                break;
            case 'Countdown':
                this.startCountdown();
                break;
            case 'Instruction':
                this.showInstruction();
                break;
            case 'Done':
                this.complete();
                break;
        }
        this.currentState = newState;
    }

    startCountdown() {
        let countdownTime = this.countdownTime;
        this.countdownDisplay.textContent = `Starting in ${countdownTime} seconds`;
        this.startButton.style.display = 'none';
        this.countdownDisplay.style.display = 'flex';
        this.instructionDisplay.style.display = 'none';
        const countdownInterval = setInterval(() => {
            this.countdownDisplay.textContent = `Starting in ${--countdownTime} seconds`;
            if (countdownTime < 0) {
                clearInterval(countdownInterval);
                this.transition('Instruction');
            }
        }, 1000);
    }

    showInstruction() {
        this.countdownDisplay.style.display = 'none';
        this.instructionDisplay.style.display = 'flex';
        const instruction = this.instructions[this.currentInstructionIndex];
        this.instructionDisplay.textContent = instruction.text;
        this.socket.emit('start_recording', {
            instruction,
            duration: this.recordingTime,
            round: this.currentRound,
            session: this.session
        });

        this.socket.once('stop_recording', () => {
            this.currentInstructionIndex++;
            if (this.currentInstructionIndex < this.instructions.length) {
                this.transition('Countdown');
            } else if (++this.currentRound < this.numRounds) {
                this.instructionDisplay.textContent = 'Round completed. Get ready for the next round.';
                setTimeout(() => { ,
                    this.currentInstructionIndex = 0;
                    this.transition('Countdown');
                }, 1000);
            } else {
                this.transition('Done');
            }
        });
    }

    complete() {
        this.instructionDisplay.textContent = '';
        this.currentState = 'Configuration';
        this.currentInstructionIndex = 0; // Reset for a new run
        this.currentRound = 0; // Reset for a new run
        // Optionally, you can add a "Done" message before showing the config screen again
        alert("All instructions completed. Configure for a new run.");
        this.transition('Configuration');
    }
}

const sm = new InstructionStateMachine();

