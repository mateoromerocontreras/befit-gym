import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Menu, X, Scale, CreditCard, Dumbbell } from 'lucide-react';

const LandingPage = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  return (
    <div className="min-h-screen bg-gray-950">
      {/* Navbar */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-gray-900/95 backdrop-blur-sm border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex-shrink-0">
              <Link to="/" className="text-2xl font-bold text-accent-lime">
                GymFlow
              </Link>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:block">
              <div className="ml-10 flex items-baseline space-x-8">
                <Link
                  to="/"
                  className="text-gray-300 hover:text-accent-lime transition-colors duration-200 px-3 py-2 text-sm font-medium"
                >
                  Inicio
                </Link>
                <Link
                  to="/rutinas"
                  className="text-gray-300 hover:text-accent-lime transition-colors duration-200 px-3 py-2 text-sm font-medium"
                >
                  Rutinas
                </Link>
                <Link
                  to="/planes"
                  className="text-gray-300 hover:text-accent-lime transition-colors duration-200 px-3 py-2 text-sm font-medium"
                >
                  Planes
                </Link>
              </div>
            </div>

            {/* Login Button */}
            <div className="hidden md:block">
              <Link
                to="/login"
                className="px-6 py-2 rounded-full border-2 border-accent-lime text-accent-lime hover:bg-accent-lime hover:text-gray-950 transition-all duration-200 font-medium"
              >
                Login
              </Link>
            </div>

            {/* Mobile menu button */}
            <div className="md:hidden">
              <button
                onClick={toggleMenu}
                className="text-gray-300 hover:text-accent-lime focus:outline-none focus:text-accent-lime"
                aria-label="Toggle menu"
              >
                {isMenuOpen ? (
                  <X className="h-6 w-6" />
                ) : (
                  <Menu className="h-6 w-6" />
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1 bg-gray-900 border-t border-gray-800">
              <Link
                to="/"
                className="block px-3 py-2 text-gray-300 hover:text-accent-lime hover:bg-gray-800 rounded-md transition-colors duration-200"
                onClick={() => setIsMenuOpen(false)}
              >
                Inicio
              </Link>
              <Link
                to="/rutinas"
                className="block px-3 py-2 text-gray-300 hover:text-accent-lime hover:bg-gray-800 rounded-md transition-colors duration-200"
                onClick={() => setIsMenuOpen(false)}
              >
                Rutinas
              </Link>
              <Link
                to="/planes"
                className="block px-3 py-2 text-gray-300 hover:text-accent-lime hover:bg-gray-800 rounded-md transition-colors duration-200"
                onClick={() => setIsMenuOpen(false)}
              >
                Planes
              </Link>
              <Link
                to="/login"
                className="block px-3 py-2 mt-4 text-center rounded-full border-2 border-accent-lime text-accent-lime hover:bg-accent-lime hover:text-gray-950 transition-all duration-200 font-medium"
                onClick={() => setIsMenuOpen(false)}
              >
                Login
              </Link>
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold mb-6 bg-gradient-to-r from-accent-lime to-accent-electric bg-clip-text text-transparent">
            Entrena con Inteligencia
          </h1>
          <p className="text-xl sm:text-2xl text-gray-400 max-w-3xl mx-auto mb-10 leading-relaxed">
            Gestiona tus créditos, sigue tus rutinas personalizadas y alcanza tus objetivos
            de forma inteligente. Tu gimnasio, tu progreso, tu control.
          </p>
          <Link
            to="/register"
            className="inline-block px-8 py-4 bg-accent-lime text-gray-950 font-bold text-lg rounded-full hover:bg-accent-electric hover:scale-105 transition-all duration-200 shadow-lg shadow-accent-lime/50"
          >
            Empieza tu cambio
          </Link>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-900/50">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-4xl font-bold text-center mb-16 text-gray-100">
            Características Principales
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="bg-gray-900 p-8 rounded-xl border border-gray-800 hover:border-accent-lime transition-all duration-300 hover:shadow-lg hover:shadow-accent-lime/20">
              <div className="flex justify-center mb-6">
                <div className="p-4 bg-accent-lime/10 rounded-full">
                  <Scale className="h-12 w-12 text-accent-lime" />
                </div>
              </div>
              <h3 className="text-2xl font-bold mb-4 text-gray-100 text-center">
                Seguimiento de Peso y Altura
              </h3>
              <p className="text-gray-400 text-center leading-relaxed">
                Registra y visualiza tu progreso físico de manera sencilla. Mantén un
                historial completo de tu evolución.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-gray-900 p-8 rounded-xl border border-gray-800 hover:border-accent-lime transition-all duration-300 hover:shadow-lg hover:shadow-accent-lime/20">
              <div className="flex justify-center mb-6">
                <div className="p-4 bg-accent-lime/10 rounded-full">
                  <CreditCard className="h-12 w-12 text-accent-lime" />
                </div>
              </div>
              <h3 className="text-2xl font-bold mb-4 text-gray-100 text-center">
                Gestión de Créditos y Suscripción
              </h3>
              <p className="text-gray-400 text-center leading-relaxed">
                Controla tus créditos de entrenamiento y gestiona tu suscripción de forma
                transparente y eficiente.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-gray-900 p-8 rounded-xl border border-gray-800 hover:border-accent-lime transition-all duration-300 hover:shadow-lg hover:shadow-accent-lime/20">
              <div className="flex justify-center mb-6">
                <div className="p-4 bg-accent-lime/10 rounded-full">
                  <Dumbbell className="h-12 w-12 text-accent-lime" />
                </div>
              </div>
              <h3 className="text-2xl font-bold mb-4 text-gray-100 text-center">
                Rutinas Personalizadas
              </h3>
              <p className="text-gray-400 text-center leading-relaxed">
                Accede a rutinas diseñadas específicamente para ti por tu administrador.
                Entrena con un plan adaptado a tus necesidades.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 border-t border-gray-800 py-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="mb-4 md:mb-0">
              <p className="text-gray-400 text-sm">
                © {new Date().getFullYear()} GymFlow. Todos los derechos reservados.
              </p>
            </div>
            <div className="flex space-x-6">
              <Link
                to="/"
                className="text-gray-400 hover:text-accent-lime transition-colors duration-200 text-sm"
              >
                Inicio
              </Link>
              <Link
                to="/rutinas"
                className="text-gray-400 hover:text-accent-lime transition-colors duration-200 text-sm"
              >
                Rutinas
              </Link>
              <Link
                to="/planes"
                className="text-gray-400 hover:text-accent-lime transition-colors duration-200 text-sm"
              >
                Planes
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
