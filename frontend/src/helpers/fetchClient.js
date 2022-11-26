import axios from 'axios';

const fetchClient = () => {
  const defaultOptions = {
    baseURL: process.env.REACT_APP_API_PATH,
    method: 'get',
    headers: {
      'Content-Type': 'application/json',
    },
  };

  // Create instance
  let instance = axios.create(defaultOptions);

  // Set the AUTH token for any request
  instance.interceptors.request.use(function (config) {
    const token = localStorage.getItem('access_token');
    config.headers.Authorization =  token ? `Bearer ${token}` : '';
    // console.log(config.headers)
    return config;
  });

  return instance;
};

export default fetchClient();