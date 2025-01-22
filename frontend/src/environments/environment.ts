interface Environment {
  apiUrl: string;
  wsUrl: string;
}

// export const environment: Environment = {
//   apiUrl: import.meta.env.VITE_API_URL,
//   wsUrl: import.meta.env.VITE_WS_URL
// }; 
export const environment = {
    apiUrl: 'http://localhost:8000',
    wsUrl: 'http://localhost:8000'  // Socket.IO will handle the path
}; 