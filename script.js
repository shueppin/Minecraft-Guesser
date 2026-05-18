const config = window.GAME_CONFIG;
const fieldConfig = window.GAME_FIELDS_CONFIG;

const searchInput = document.getElementById('searchInput');
const searchResults = document.getElementById('searchResults');
const guessTable = document.getElementById('guessTable');
const scoreContainer = document.getElementById('scoreContainer');
const searchHeader = document.getElementById('searchHeader');

let allData = {};
let mysteryKey = null;
let mysteryObject = null;
let guesses = [];
let guessedKeys = [];
let gameFinished = false;

const MAX_SCORE = 100;
const MIN_SCORE = 1;
const SCORE_DEDUCTION_PER_GUESS = 8;

init();

async function init() {
    const response = await fetch(config.dataFile);
    allData = await response.json();

    setupDailyObject();
    renderSearchHeader();
    renderGuessTableHead();
    loadGuesses();

    searchInput.addEventListener('input', updateSearchResults);
}

function getDateSeed() {
    const d = new Date();
    return `${d.getUTCFullYear()}-${d.getUTCMonth()}-${d.getUTCDate()}-${config.type}`;
}

function seededRandom(seed) {
    let h = 2166136261;

    for (let i = 0; i < seed.length; i++) {
        h ^= seed.charCodeAt(i);
        h = Math.imul(h, 16777619);
    }

    return Math.abs(h);
}

function setupDailyObject() {
    const keys = Object.keys(allData);

    const seed = seededRandom(getDateSeed());

    const index = seed % keys.length;

    mysteryKey = keys[index];
    mysteryObject = allData[mysteryKey];
}

function renderGuessTableHead() {
    const guessTableHead = document.getElementById('guessTableHead');

    guessTableHead.innerHTML = `
        <th>${config.displayName}</th>
        ${fieldConfig.map(f => `<th>${f.label}</th>`).join('')}
    `;
}

function storageKey() {
    return `${config.type}-${getDateSeed()}`;
}

function loadGuesses() {
    const saved = JSON.parse(localStorage.getItem(storageKey()) || '[]');

    guesses = saved;

    guesses.forEach(key => {
        guessedKeys.push(key);
        renderGuess(key);
    });

    if (guessedKeys.includes(mysteryKey)) {
        gameFinished = true;
        finishGame();
    }
}

function saveGuesses() {
    localStorage.setItem(storageKey(), JSON.stringify(guesses));
}

function renderSearchHeader() {
    document.querySelector('.search-wrapper')
        .style.setProperty('--field-count', fieldConfig.length);

    searchHeader.innerHTML = `
        <div>${config.displayName}</div>
        ${fieldConfig.map(f => `<div>${f.label}</div>`).join('')}
    `;
}

function updateSearchResults() {
    const query = searchInput.value.toLowerCase().trim();

    searchResults.innerHTML = '';

    if (!query) {
        searchHeader.style.display = 'none';
        return;
    }

    searchHeader.style.display = 'grid';

    const entries = Object.entries(allData)
        .filter(([key, obj]) => {
            return obj.title.toLowerCase().includes(query)
                && !guessedKeys.includes(key);
        })
        .sort((a, b) => {
            const aTitle = a[1].title.toLowerCase();
            const bTitle = b[1].title.toLowerCase();

            const aStarts = aTitle.startsWith(query);
            const bStarts = bTitle.startsWith(query);

            if (aStarts && !bStarts) return -1;
            if (!aStarts && bStarts) return 1;

            return aTitle.localeCompare(bTitle);
        })
        .slice(0, 10);

    if (entries.length === 0) {
        searchHeader.style.display = 'none';
        return;
    }

    entries.forEach(([key, obj]) => {

        const div = document.createElement('div');
        div.className = 'result-item';

        let previewFields = '';

        fieldConfig.forEach(({ key, label }) => {

            let value = obj[key];

            if (Array.isArray(value)) {
                value = value.join(', ');
            }

            if (typeof value === 'boolean') {
                value = value ? 'Yes' : 'No';
            }

            previewFields += `
                <div class="preview-cell">
                    ${value}
                </div>
            `;
        });

        div.innerHTML = `
            <div class="result-main">
                <img src="${obj.image_url}">
                <span>${obj.title}</span>
            </div>
            ${previewFields}
        `;

        div.addEventListener('click', () => {
            if (gameFinished) return;
            makeGuess(key);
        });

        searchResults.appendChild(div);
    });
}

function makeGuess(key) {

    if (gameFinished) return;

    if (guessedKeys.includes(key)) return;

    guessedKeys.push(key);
    guesses.push(key);

    saveGuesses();

    renderGuess(key);

    searchInput.value = '';
    searchResults.innerHTML = '';

    searchHeader.style.display = 'none';

    if (key === mysteryKey) {
        finishGame();
    }
}

function renderGuess(key) {

    const obj = allData[key];

    const row = document.createElement('tr');

    const imageCell = document.createElement('td');
    imageCell.className = 'guess-cell';

    imageCell.innerHTML = `
        <img class="guess-image" src="${obj.image_url}">
        <div>${obj.title}</div>
    `;

    row.appendChild(imageCell);

    fieldConfig.forEach(({ key, label }) => { // Iterate over all fields
        const td = document.createElement('td');

        const comparison = compareField(key, obj[key], mysteryObject[key]);

        td.classList.add(comparison.status);

        if (comparison.arrow) {
            td.classList.add(comparison.arrow);
        }

        td.innerHTML = comparison.display;

        row.appendChild(td);
    });

    guessTable.prepend(row);
}

function compareField(field, value, target) {

    if (Array.isArray(value)) {

        const overlap = value.filter(v => target.includes(v));

        if (overlap.length === target.length && value.length === target.length) {
            return {
                status: 'correct',
                display: value.join(', ')
            };
        }

        if (overlap.length > 0) {
            return {
                status: 'partial',
                display: value.join(', ')
            };
        }

        return {
            status: 'wrong',
            display: value.join(', ')
        };
    }

    if (typeof value === 'number') {

        if (value === target) {
            return {
                status: 'correct',
                display: value
            };
        }

        return {
            status: 'wrong',
            display: value,
            arrow: value < target ? 'arrow-up' : 'arrow-down'
        };
    }

    if (typeof value === 'boolean') {

        return {
            status: value === target ? 'correct' : 'wrong',
            display: value ? 'Yes' : 'No'
        };
    }

    if (field === 'initial_release') {

        const valueNumber = parseMinecraftVersion(value);
        const targetNumber = parseMinecraftVersion(target);

        if (valueNumber.join('.') === targetNumber.join('.')) {
            return {
                status: 'correct',
                display: value
            };
        }

        let arrow = null;

        for (let i = 0; i < 3; i++) {
            if (valueNumber[i] < targetNumber[i]) {
                arrow = 'arrow-up';
                break;
            }
            if (valueNumber[i] > targetNumber[i]) {
                arrow = 'arrow-down';
                break;
            }
        }

        return {
            status: 'wrong',
            display: value,
            arrow
        };
    }

    if (value === target) {
        return {
            status: 'correct',
            display: value
        };
    }

    const valParts = String(value).split(',').map(v => v.trim());
    const targetParts = String(target).split(',').map(v => v.trim());

    const overlap = valParts.filter(v => targetParts.includes(v));

    if (overlap.length > 0) {
        return {
            status: 'partial',
            display: value
        };
    }

    return {
        status: 'wrong',
        display: value
    };
}

function parseMinecraftVersion(version) {
    // Pre-alpha is [0, 0, 0], Alpha is [0.1, ..., ...], Beta is [0.2, ..., ...]
    if (!version) return [0, 0, 0];

    version = version.toLowerCase();
 
    if (version === "pre-alpha") {
        return [0, 0, 0]
    }

    // Beta / Alpha handling
    if (version.includes("alpha")) {
        const nums = version.match(/\d+/g) || [0, 0, 0];
        return [0.1, parseInt(nums[1] || 0), parseInt(nums[2] || 0)];  // Replace the 1. with a 0.1
    }

    if (version.includes("beta")) {
        const nums = version.match(/\d+/g) || [0, 0, 0];
        return [0.2, parseInt(nums[1] || 0), parseInt(nums[2] || 0)];  // Replace the 1. with a 0.1
    }

    // Normal versions like 1.20, 1.20.1
    const parts = version.match(/\d+/g) || [0, 0, 0];

    return [
        parseInt(parts[0] || 0),
        parseInt(parts[1] || 0),
        parseInt(parts[2] || 0)
    ];
}

function finishGame() {

    gameFinished = true;

    const guessesNeeded = guesses.length;

    let score = MAX_SCORE - ((guessesNeeded - 1) * SCORE_DEDUCTION_PER_GUESS);

    score = Math.max(MIN_SCORE, score);

    scoreContainer.innerHTML = `
        <div class="finished">
            You found today's ${config.type.slice(0, -1)}!<br>
            Score: ${score}/100<br>
            Guesses: ${guessesNeeded}
        </div>
    `;
}