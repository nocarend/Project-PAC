import React, { useState } from "react";
import axios from "axios";
import { setAuthToken } from "../helpers/setAuthToken"
import fetchClient from "../helpers/fetchClient";

const Login = () => {

  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    //reqres registered sample user
    const loginPayload = {
      "username": username,
      "password": password
    }

    axios.post("/api/auth/login", loginPayload)
      .then(response => {
        console.log(response)
        //get token from response
        const token = response.data.access_token;
        //set JWT token to local
        localStorage.setItem("access_token", token);

        //set token to axios common header
        // setAuthToken(token);
        // console.log(axios.defaults.headers)

        //redirect user to home page
        window.location.href = '/home'

      })
      .catch(err => console.log(err));
  };
  const handleUsernameChange = (e) => {
    setUsername(e.target.value)
  }

  const handlePasswordChange = (e) => {
    setPassword(e.target.value)
  }

  return (
    <div>
      <h2>Login</h2>
      <form action="#">
        <div>
          <input type="text" 
            placeholder="Username" 
            onChange={handleUsernameChange}
            value={username} 
          />
        </div>
        <div>
          <input
            type="password"
            placeholder="Password"
            onChange={handlePasswordChange}
            value={password}
          />
        </div>
        <button onClick={handleSubmit} type="submit">
          Login Now
        </button>
      </form>
    </div>
  );
}
export default Login