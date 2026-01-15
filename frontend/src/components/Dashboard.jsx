import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Dashboard = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <div className="min-vh-100 bg-light">
            <nav className="navbar navbar-expand-lg navbar-dark bg-primary">
                <div className="container">
                    <a className="navbar-brand" href="#">
                        <i className="bi bi-dumbbell me-2"></i>
                        Befit Gym
                    </a>
                    <button
                        className="btn btn-outline-light"
                        onClick={handleLogout}
                    >
                        <i className="bi bi-box-arrow-right me-2"></i>
                        Logout
                    </button>
                </div>
            </nav>

            <div className="container mt-5">
                <div className="row">
                    <div className="col-12">
                        <div className="card shadow-sm">
                            <div className="card-body p-5">
                                <h1 className="display-4 mb-4">
                                    Welcome to Befit Gym! 💪
                                </h1>
                                <div className="alert alert-success" role="alert">
                                    <h4 className="alert-heading">
                                        <i className="bi bi-check-circle me-2"></i>
                                        Successfully Logged In!
                                    </h4>
                                    <p className="mb-0">
                                        You're now authenticated and ready to start your fitness journey.
                                    </p>
                                </div>

                                <div className="card mt-4">
                                    <div className="card-header bg-primary text-white">
                                        <h5 className="mb-0">
                                            <i className="bi bi-person-circle me-2"></i>
                                            Your Profile
                                        </h5>
                                    </div>
                                    <div className="card-body">
                                        <div className="row">
                                            <div className="col-md-6">
                                                <p className="mb-2">
                                                    <strong>Email:</strong> {user?.email}
                                                </p>
                                                <p className="mb-2">
                                                    <strong>User ID:</strong> {user?.id}
                                                </p>
                                                <p className="mb-0">
                                                    <strong>Member Since:</strong>{' '}
                                                    {user?.date_joined && new Date(user.date_joined).toLocaleDateString()}
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div className="row mt-4">
                                    <div className="col-md-4 mb-3">
                                        <div className="card text-center h-100">
                                            <div className="card-body">
                                                <i className="bi bi-activity display-1 text-primary"></i>
                                                <h5 className="card-title mt-3">Workouts</h5>
                                                <p className="card-text text-muted">
                                                    Track your fitness progress
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="col-md-4 mb-3">
                                        <div className="card text-center h-100">
                                            <div className="card-body">
                                                <i className="bi bi-calendar-check display-1 text-success"></i>
                                                <h5 className="card-title mt-3">Schedule</h5>
                                                <p className="card-text text-muted">
                                                    Book your gym sessions
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="col-md-4 mb-3">
                                        <div className="card text-center h-100">
                                            <div className="card-body">
                                                <i className="bi bi-graph-up display-1 text-info"></i>
                                                <h5 className="card-title mt-3">Progress</h5>
                                                <p className="card-text text-muted">
                                                    View your achievements
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
