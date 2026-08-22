import { BrowserRouter } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import AppRouter from './router';

export default function App() {
  return (
    <BrowserRouter>
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            fontFamily: 'Inter, sans-serif',
            fontSize: '14px',
            borderRadius: '8px',
            background: '#001c40',
            color: '#ffffff',
          },
          success: {
            iconTheme: { primary: '#10B981', secondary: '#ffffff' },
          },
          error: {
            iconTheme: { primary: '#ba1a1a', secondary: '#ffffff' },
          },
        }}
      />
      <AppRouter />
    </BrowserRouter>
  );
}
