import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Register = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [password2, setPassword2] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    const { register } = useAuth();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (password !== password2) {
            setError('Passwords do not match');
            return;
        }

        setLoading(true);
        const result = await register(email, password, password2);
        setLoading(false);

        if (result.success) {
            navigate('/dashboard');
        } else {
            setError(result.message);
        }
    };

    return (
        <div className="container">
            <div className="row justify-content-center mt-5">
                <div className="col-md-6 col-lg-5">
                    <div className="card shadow">
                        <div className="card-body p-5">
                            <h2 className="text-center mb-4">
                                <i className="bi bi-person-plus me-2"></i>
                                Create Account
                            </h2>

                            {error && (
                                <div className="alert alert-danger" role="alert">
                                    {error}
                                </div>
                            )}

                            <form onSubmit={handleSubmit}>
                                <div className="mb-3">
                                    <label htmlFor="email" className="form-label">Email address</label>
                                    <input
                                        type="email"
                                        className="form-control"
                                        id="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        required
                                        autoComplete="email"
                                        placeholder="Enter your email"
                                    />
                                    <div className="form-text">We'll never share your email with anyone else.</div>
                                </div>

                                <div className="mb-3">
                                    <label htmlFor="password" className="form-label">Password</label>
                                    <input
                                        type="password"
                                        className="form-control"
                                        id="password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        required
                                        autoComplete="new-password"
                                        placeholder="Enter your password"
                                        minLength="8"
                                    />
                                    <div className="form-text">Password must be at least 8 characters.</div>
                                </div>

                                <div className="mb-3">
                                    <label htmlFor="password2" className="form-label">Confirm Password</label>
                                    <input
                                        type="password"
                                        className="form-control"
                                        id="password2"
                                        value={password2}
                                        onChange={(e) => setPassword2(e.target.value)}
                                        required
                                        autoComplete="new-password"
                                        placeholder="Confirm your password"
                                        minLength="8"
                                    />
                                </div>

                                <button
                                    type="submit"
                                    className="btn btn-success w-100 mb-3"
                                    disabled={loading}
                                >
                                    {loading ? (
                                        <>
                                            <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                                            Creating account...
                                        </>
                                    ) : (
                                        'Register'
                                    )}
                                </button>
                            </form>

                            <div className="text-center">
                                <p className="mb-0">
                                    Already have an account?{' '}
                                    <Link to="/login" className="text-decoration-none">
                                        Login here
                                    </Link>
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Register;
