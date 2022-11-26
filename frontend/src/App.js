import './App.css';
import axios from 'axios'
import Login from './pages/Login';
// import Routes1 from './routes'
import { history } from './helpers/history';
import { Routes, Route, BrowserRouter as Router, Navigate } from 'react-router-dom';
import { setAuthToken } from './helpers/setAuthToken'
import NoHome from './pages/Nohome';
import Home from './pages/Home';

const App = () => {

  // check jwt token
  // const token = localStorage.getItem("access_token");
  // if (token) {
  //   setAuthToken(token);
  // }


  return (
    <Router history={history}>
      <Routes>
        <Route
          path="/login" element={<Login />} />
        <Route path="/nohome" element={<NoHome />} />
        <Route path="/home" element={<Home />} />
        <Route path="/*" element={<Navigate to="/nohome" />} />
      </Routes>
    </Router>)
}

export default App;