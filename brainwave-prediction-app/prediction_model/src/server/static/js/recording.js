DEFAULT_INSTRUCTIONS = [
    {text: 'Drone go left', label: 'left'},
    {text: 'Drone go right', label: 'right'},
    {text: 'Drone go takeoff', label: 'takeoff'},
    {text: 'Drone go land', label: 'land'},
    {text: 'Drone go forward', label: 'forward'},
    {text: 'Drone go backward', label: 'backward'}
]

class Config {
    /**
     * Configuration object for the recording state machine
     * @param {Array<{text: string, label: string}>} instructions - The instructions to be recorded
     * @param {number} countdownTime - The time to wait before starting the recording
     * @param {number} recordingTime - The time to record each instruction
     * @param {number} numRounds - The number of rounds to record
     */
    constructor(instructions, countdownTime, recordingTime, numRounds) {
        this.instructions = instructions
        this.countdownTime = countdownTime
        this.recordingTime = recordingTime
        this.numRounds = numRounds
    }

    save() {
        console.log('Saving configuration');
        localStorage.setItem('config', JSON.stringify(this));
    }

    static load() {
        let config = JSON.parse(localStorage.getItem('config'));
        return config
            ? new Config(config.instructions, config.countdownTime, config.recordingTime, config.numRounds)
            : Config.defaultConfig();
    }

    static defaultConfig() {
        console.log('Loading default configuration');
        let instructions = JSON.parse(JSON.stringify(DEFAULT_INSTRUCTIONS));
        return new Config(instructions, 5, 5, 3);
    }
}

class InstructionStateMachine {
    Screens = Object.freeze({
        CONFIG: 0,
        // RECORDING: 1,
        READY: 2,
        COUNTDOWN: 3,
        INSTRUCTION: 4,
        COMPLETE: 5,
    });

    States = Object.freeze({
        IDLE: 0,
        CONFIGURATION: 1,
        READY: 2,
        COUNTDOWN: 3,
        INSTRUCTION: 4,
        DONE: 5,
    });

    constructor() {
        this.socket = io.connect('http://' + document.domain + ':' + location.port);
        this.currentState = this.States.IDLE;
        this.config = Config.load();
        this.recordingParams = this.resetRecordingParams(true);
        this.configScreenElements = this.getConfigScreenElements();
        this.recordingScreenElements = this.getRecordingScreenElements();
        this.completeScreenElements = this.getCompleteScreenElements();
        this.transition(this.States.CONFIGURATION);
    }

    /**
     * Reset the recording parameters
     * @param {boolean} [newSession=false] - Whether to start a new session
     * @returns {{currentRound: number, session: float, currentInstructionIndex: number}}
     */
    resetRecordingParams(newSession = false) {
        return {
            currentRound: 1,
            currentInstructionIndex: 0,
            session: newSession ? (new Date().getTime()) : this.recordingParams.session
        };
    }

    clearDisplays() {
        this.recordingScreenElements.countdownDisplay.textContent = '';
        this.recordingScreenElements.countdownMessage.textContent = '';
        this.recordingScreenElements.countdownTimer.textContent = '';
        this.recordingScreenElements.instructionDisplay.textContent = '';
    }

    /**
     * bind the configuration elements from the config screen to an object
     * @returns {{countdownLength: HTMLElement, instructionsContainer: HTMLElement, addInstruction: HTMLElement,
     *            recordingTime: HTMLElement, configScreen: HTMLElement,
     *            startConfig: HTMLElement, numberOfRounds: HTMLElement,
     *            clearInstructions: HTMLElement}}
     */
    getConfigScreenElements() {
        return {
            configScreen: document.getElementById('configScreen'),
            numberOfRounds: document.getElementById('numberOfRounds'),
            countdownLength: document.getElementById('countdownLength'),
            recordingTime: document.getElementById('recordingTime'),
            instructionsContainer: document.getElementById('instructionsContainer'),
            addInstruction: document.getElementById('addInstruction'),
            startConfig: document.getElementById('startConfig'),
            clearInstructions: document.getElementById('clearInstructions')
        }
    }

    /**
     * bind the recording elements from the DOM to an object
     * @returns {{
     *   recordingScreen: HTMLElement, readyScreen: HTMLElement, startButton: HTMLElement,
     *   countdownScreen: HTMLElement, countdownDisplay: HTMLElement, countdownMessage: HTMLElement, countdownTimer: HTMLElement,
     *   instructionScreen: HTMLElement, instructionDisplay: HTMLElement,
     *   cancelBtn: HTMLElement }}
     */
    getRecordingScreenElements() {
        return {
            recordingScreen: document.getElementById('recordingScreen'),
            readyScreen: document.getElementById('readyScreen'),
            startButton: document.getElementById('startButton'),
            countdownScreen: document.getElementById('countdownScreen'),
            countdownDisplay: document.getElementById('countdownDisplay'),
            countdownMessage: document.getElementById('countdownMessage'),
            countdownTimer: document.getElementById('countdownTimer'),
            instructionScreen: document.getElementById('instructionScreen'),
            instructionDisplay: document.getElementById('instructionDisplay'),
            cancelBtn: document.getElementById('cancelBtn')
        }
    }

    /**
     *
     * @returns {{newSessionBtn: HTMLElement, sameSessionBtn: HTMLElement, completeScreen: HTMLElement}}
     */
    getCompleteScreenElements() {
        return {
            completeScreen: document.getElementById('completeScreen'),
            sameSessionBtn: document.getElementById('sameSessionBtn'),
            newSessionBtn: document.getElementById('newSessionBtn')
        }
    }

    clearInstructions() {
        this.configScreenElements.instructionsContainer
            .querySelectorAll('.instructionInput')
            .forEach((elem) => {
                elem.remove();
            });
    }

    /**
     * Add an instruction input to the configuration screen
     * @param {string} [instructionText=] - The instruction text to display in the input
     * @param {string} [instructionLabel=] - The instruction label to display in the input
     */
    addInstructionInput(instructionText = '', instructionLabel = '') {
        console.log('Adding instruction input');
        const instructionDiv = `
            <div class="row mb-3 instructionInput justify-content-center py-1">
                <div class="col-6 ">
                    <input type="text" data-ins-type="text" class="form-control" placeholder="Instruction Text" value="${instructionText}">
                </div>
                <div class="col-6">
                    <input type="text" data-ins-type="label" class="form-control" placeholder="Instruction Label" value="${instructionLabel}">
                </div>
            </div>
        `
        this.configScreenElements.instructionsContainer.innerHTML += instructionDiv;
    }

    acceptConfig() {
        console.log('Accepting configuration');
        this.config = this.configFromInputs();
        this.config.save();

        if (this.instructions.length > 0) {
            this.transition(this.States.READY);
        } else {
            alert("Please add at least one instruction with its label.");
        }
    }

    /**
     * Populate a configuration object from the input fields
     * @returns {Config}
     */
    configFromInputs() {
        const instructionElements =
            this.configScreenElements.instructionsContainer.getElementsByClassName('instructionInput');
        this.instructions = Array.from(instructionElements).map(elem => ({
            text: elem.querySelector('[data-ins-type="text"]').value,
            label: elem.querySelector('[data-ins-type="label"]').value
        })).filter(instr => instr.text && instr.label);

        let countdownTime = this.configScreenElements.countdownLength.value;
        let recordingTime = this.configScreenElements.recordingTime.value;
        let numRounds = this.configScreenElements.numberOfRounds.value;

        return new Config(this.instructions, countdownTime, recordingTime, numRounds);
    }

    hideElements(...elements) {
        elements.forEach((element) => element.classList.add('d-none'));
    }

    showElements(...elements) {
        elements.forEach((element) => element.classList.remove('d-none'));
    }

    /**
     *
     * @param {number} screen
     */
    switchScreen(screen) {
        this.hideElements(
            this.configScreenElements.configScreen,
            this.recordingScreenElements.recordingScreen,
            this.recordingScreenElements.readyScreen,
            this.recordingScreenElements.countdownScreen,
            this.recordingScreenElements.instructionScreen,
            this.completeScreenElements.completeScreen
        );

        switch (screen) {
            case this.Screens.CONFIG:
                console.log('Showing screen for CONFIG')
                this.showElements(this.configScreenElements.configScreen);
                break;
            case this.Screens.READY:
                console.log('Showing screen for READY')
                this.showElements(
                    this.recordingScreenElements.recordingScreen,
                    this.recordingScreenElements.readyScreen
                );
                break;
            case this.Screens.COUNTDOWN:
                console.log('Showing screen for COUNTDOWN')
                this.showElements(
                    this.recordingScreenElements.recordingScreen,
                    this.recordingScreenElements.countdownScreen
                );
                break;
            case this.Screens.INSTRUCTION:
                console.log('Showing screen for INSTRUCTION')
                this.showElements(
                    this.recordingScreenElements.recordingScreen,
                    this.recordingScreenElements.instructionScreen
                );
                break;
            case this.Screens.COMPLETE:
                console.log('Showing screen for COMPLETE')
                this.showElements(this.completeScreenElements.completeScreen);
                break;
            default:
                console.error('Invalid screen');
        }
    }

    showConfigScreen() {
        this.switchScreen(this.Screens.CONFIG);

        this.configScreenElements.startConfig.onclick = () => this.acceptConfig();
        this.configScreenElements.addInstruction.onclick = () => this.addInstructionInput();

        this.configScreenElements.clearInstructions.onclick = () => {
            this.clearInstructions();
        }

        // listen for input changes and save to local storage
        this.configScreenElements.configScreen.onchange = () => {
            this.config = this.configFromInputs();
            this.config.save();
        }

        this.configScreenElements.numberOfRounds.value = this.config.numRounds;
        this.configScreenElements.countdownLength.value = this.config.countdownTime;
        this.configScreenElements.recordingTime.value = this.config.recordingTime;

        this.clearInstructions();
        for (let instruction of this.config.instructions) {
            this.addInstructionInput(instruction.text, instruction.label);
        }
    }

    showReadyScreen() {
        this.switchScreen(this.Screens.READY);
        this.recordingScreenElements.startButton.addEventListener('click', () => {
            this.transition(this.States.COUNTDOWN);
        }, {once: true});
    }

    showCountdownScreen() {
        this.switchScreen(this.Screens.COUNTDOWN);
        this.recordingScreenElements.cancelBtn.disabled = true;
        const countdownInterval = this.showCountdown();
        this.recordingScreenElements.cancelBtn.disabled = false;
        this.recordingScreenElements.cancelBtn.onclick = () => {
            clearInterval(countdownInterval);
            this.transition(this.States.CONFIGURATION);
        }
    }

    showInstructionScreen() {
        this.switchScreen(this.Screens.INSTRUCTION);
        this.showInstruction();
        this.recordingScreenElements.cancelBtn.onclick = () => {
            this.socket.emit('cancel_recording');

            this.socket.once('cancel_success', () => {
                this.transition(this.States.CONFIGURATION);
            });
        }
    }

    showCompleteScreen() {
        this.switchScreen(this.Screens.COMPLETE);
        this.clearDisplays();
        this.completeScreenElements.newSessionBtn.onclick = () => {
            this.recordingParams = this.resetRecordingParams(true);
            this.transition(this.States.CONFIGURATION);
        }
        this.completeScreenElements.sameSessionBtn.onclick = () => {
            this.transition(this.States.CONFIGURATION);
        }
    }

    /**
     *
     * @param {number} newState
     */
    transition(newState) {
        switch (newState) {
            case this.States.IDLE:
                break;
            case this.States.CONFIGURATION:
                this.showConfigScreen();
                break;
            case this.States.READY:
                this.showReadyScreen();
                break;
            case this.States.COUNTDOWN:
                this.showCountdownScreen();
                break;
            case this.States.INSTRUCTION:
                this.showInstructionScreen();
                break;
            case this.States.DONE:
                this.showCompleteScreen();
                break;
            default:
                console.error('Invalid state');
        }
        this.currentState = newState;
    }


    showCountdown(message = 'Next Instruction In:') {
        console.log(`message: ${message}`);
        let countdownTime = this.config.countdownTime;
        this.recordingScreenElements.countdownMessage.textContent = message;
        this.recordingScreenElements.countdownTimer.textContent = `${countdownTime}`;

        const countdownInterval = setInterval(() => {
            this.recordingScreenElements.countdownTimer.textContent = `${--countdownTime}`;
            if (countdownTime <= 0) {
                clearInterval(countdownInterval);
                this.transition(this.States.INSTRUCTION);
            }
        }, 1000);

        return countdownInterval;
    }

    showInstruction() {
        const instruction = this.instructions[this.recordingParams.currentInstructionIndex];

        this.recordingScreenElements.instructionDisplay.textContent = instruction.text;

        this.socket.emit('start_recording', {
            instruction,
            duration: this.config.recordingTime,
            round: this.recordingParams.currentRound,
            session: this.recordingParams.session
        });

        this.socket.once('stop_recording', () => {
            this.recordingParams.currentInstructionIndex++;
            if (this.recordingParams.currentInstructionIndex < this.config.instructions.length) {
                this.transition(this.States.COUNTDOWN);
                console.log(`current round: ${this.recordingParams.currentRound}`);
            } else if (++this.recordingParams.currentRound <= this.config.numRounds) {
                console.log('Round completed');
                this.recordingScreenElements.instructionDisplay.textContent = 'Round completed. Click start to begin the next round.';
                this.recordingScreenElements.startButton.addEventListener('click', () => {
                    this.recordingParams.currentInstructionIndex = 0;
                    this.transition(this.States.COUNTDOWN);
                }, {once: true});
            } else {
                this.transition(this.States.DONE);
            }
        });
    }
}

const sm = new InstructionStateMachine();

