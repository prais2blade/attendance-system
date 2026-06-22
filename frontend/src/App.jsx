import {
  BrowserRouter,
  Routes,
  Route,
} from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import Students from "./pages/Students";

function App() {
  return (
    <BrowserRouter>

      <Routes>

        <Route
          path="/"
          element={<Dashboard />}
        />
        <Route
          path="/students"
          element={<Students />}
        />

      </Routes>
      
    </BrowserRouter>
  );
}

export default App;