// src/hooks/useExternalScript.js
import { useEffect, useState } from 'react';

export const useExternalScript = (url) => {
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const script = document.createElement('script');
    script.src = url;
    script.async = true;
    
    script.onload = () => {
      console.log(`Script loaded: ${url}`);
      setLoaded(true);
    };
    
    script.onerror = () => {
      console.error(`Failed to load script: ${url}`);
    };

    document.body.appendChild(script);

    return () => {
      document.body.removeChild(script);
    };
  }, [url]);

  return loaded;
};