import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { DataQuality } from './pages/DataQuality';
import { DataImport } from './pages/DataImport';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {/* Navigation */}
        <nav className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="text-2xl font-bold text-blue-600">💼 Sales 360</div>
              </div>
              <div className="flex gap-6">
                <Link to="/import" className="text-gray-700 hover:text-blue-600 font-medium">
                  Import
                </Link>
                <Link to="/data-quality" className="text-gray-700 hover:text-blue-600 font-medium">
                  Data Quality
                </Link>
                <Link to="/services" className="text-gray-700 hover:text-blue-600 font-medium">
                  Services
                </Link>
                <Link to="/opportunities" className="text-gray-700 hover:text-blue-600 font-medium">
                  Opportunities
                </Link>
                <Link to="/customers" className="text-gray-700 hover:text-blue-600 font-medium">
                  Customers
                </Link>
              </div>
            </div>
          </div>
        </nav>

        {/* Routes */}
        <Routes>
          <Route path="/import" element={<DataImport />} />
          <Route path="/data-quality" element={<DataQuality />} />
          <Route
            path="/"
            element={
              <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="text-center">
                  <h1 className="text-4xl font-bold text-gray-900 mb-4">Sales Customer 360</h1>
                  <p className="text-gray-600 text-lg">
                    Data Quality | Service Catalog | Conversion Engine
                  </p>
                  <div className="mt-8">
                    <Link
                      to="/data-quality"
                      className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
                    >
                      Start Data Quality
                    </Link>
                  </div>
                </div>
              </div>
            }
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
