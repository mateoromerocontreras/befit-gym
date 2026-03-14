import React, { useMemo, useState } from 'react';
import axios from 'axios';

const API_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/auth').replace(/\/$/, '');

const GOAL_OPTIONS = [
    'LOSE_WEIGHT',
    'GAIN_MUSCLE',
    'TONE',
    'STRENGTH',
    'ENDURANCE',
    'GENERAL_HEALTH',
];

const LEVEL_OPTIONS = ['BEGINNER', 'INTERMEDIATE', 'ADVANCED'];

const logFieldErrors = (errorData) => {
    if (!errorData || typeof errorData !== 'object') {
        console.error("'error': 'Unknown error response'");
        return;
    }

    Object.entries(errorData).forEach(([field, value]) => {
        if (Array.isArray(value)) {
            value.forEach((message) => {
                console.error(`'${field}': '${message}'`);
            });
            return;
        }

        if (value && typeof value === 'object') {
            Object.entries(value).forEach(([nestedField, nestedValue]) => {
                if (Array.isArray(nestedValue)) {
                    nestedValue.forEach((message) => {
                        console.error(`'${field}.${nestedField}': '${message}'`);
                    });
                } else {
                    console.error(`'${field}.${nestedField}': '${nestedValue}'`);
                }
            });
            return;
        }

        console.error(`'${field}': '${value}'`);
    });
};

const DebugAuth = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('Test1234!');
    const [age, setAge] = useState('28');
    const [goal, setGoal] = useState('GENERAL_HEALTH');
    const [level, setLevel] = useState('BEGINNER');
    const [running, setRunning] = useState(false);
    const [result, setResult] = useState('');

    const defaultEmail = useMemo(
        () => `qa_${Date.now()}@example.com`,
        []
    );

    const runAuthTest = async () => {
        const testEmail = email || defaultEmail;
        const registerPayload = {
            email: testEmail,
            password,
            password2: password,
            age: Number(age),
            goal,
            level,
        };

        setRunning(true);
        setResult('Running register/login test...');

        try {
            console.group('DebugAuth - Register');
            console.log('POST', `${API_URL}/register/`, registerPayload);

            const registerResponse = await axios.post(
                `${API_URL}/register/`,
                registerPayload
            );
            console.log('Register OK:', registerResponse.data);
            console.groupEnd();

            console.group('DebugAuth - Login');
            const loginPayload = { email: testEmail, password };
            console.log('POST', `${API_URL}/login/`, loginPayload);

            const loginResponse = await axios.post(`${API_URL}/login/`, loginPayload);
            console.log('Login OK:', loginResponse.data);
            console.groupEnd();

            setResult(`OK: register/login completado para ${testEmail}`);
        } catch (error) {
            console.groupEnd();
            const responseData = error?.response?.data;

            console.group('DebugAuth - Error details');
            console.error('Status:', error?.response?.status);
            console.error('Raw error:', responseData || error.message);
            logFieldErrors(responseData);
            console.groupEnd();

            setResult('Falló la prueba. Revisa la consola para errores por campo.');
        } finally {
            setRunning(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-950 text-gray-100 p-6">
            <div className="max-w-xl mx-auto bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-4">
                <h1 className="text-xl font-bold text-accent-lime">Debug Auth API</h1>
                <p className="text-sm text-gray-400">
                    Ejecuta un test de registro + login contra la API nueva en inglés.
                </p>

                <div>
                    <label htmlFor="debug-email" className="block text-sm text-gray-300 mb-1">Email (opcional)</label>
                    <input
                        id="debug-email"
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder={defaultEmail}
                        className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg"
                    />
                </div>

                <div>
                    <label htmlFor="debug-password" className="block text-sm text-gray-300 mb-1">Password</label>
                    <input
                        id="debug-password"
                        type="text"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg"
                    />
                </div>

                <div>
                    <label htmlFor="debug-age" className="block text-sm text-gray-300 mb-1">Age</label>
                    <input
                        id="debug-age"
                        type="number"
                        min="1"
                        max="120"
                        value={age}
                        onChange={(e) => setAge(e.target.value)}
                        className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg"
                    />
                </div>

                <div>
                    <label htmlFor="debug-goal" className="block text-sm text-gray-300 mb-1">Goal</label>
                    <select
                        id="debug-goal"
                        value={goal}
                        onChange={(e) => setGoal(e.target.value)}
                        className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg"
                    >
                        {GOAL_OPTIONS.map((goalValue) => (
                            <option key={goalValue} value={goalValue}>{goalValue}</option>
                        ))}
                    </select>
                </div>

                <div>
                    <label htmlFor="debug-level" className="block text-sm text-gray-300 mb-1">Level</label>
                    <select
                        id="debug-level"
                        value={level}
                        onChange={(e) => setLevel(e.target.value)}
                        className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg"
                    >
                        {LEVEL_OPTIONS.map((levelValue) => (
                            <option key={levelValue} value={levelValue}>{levelValue}</option>
                        ))}
                    </select>
                </div>

                <button
                    type="button"
                    onClick={runAuthTest}
                    disabled={running}
                    className="w-full py-2 px-4 bg-accent-lime text-gray-950 font-semibold rounded-lg disabled:opacity-60"
                >
                    {running ? 'Ejecutando...' : 'Run Debug Auth Test'}
                </button>

                {result && <p className="text-sm text-gray-300">{result}</p>}
            </div>
        </div>
    );
};

export default DebugAuth;
