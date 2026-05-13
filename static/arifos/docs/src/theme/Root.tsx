import React from 'react';

// This component wraps the entire Docusaurus application.
export default function Root({children}: {children: React.ReactNode}) {
  return <>{children}</>;
}
