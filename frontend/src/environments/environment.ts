interface Environment {
  apiUrl: string;
  wsUrl: string;
}

// export const environment: Environment = {
//   apiUrl: import.meta.env.VITE_API_URL,
//   wsUrl: import.meta.env.VITE_WS_URL
// }; 
export const environment = {
  production: false,
  apiUrl: '',  // Remove /api prefix
  wsUrl: window.location.origin  // This will be http://localhost in development
}; 