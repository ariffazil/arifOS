import React, { useEffect } from 'react';
import Layout from '@theme/Layout';

export default function Console(): JSX.Element {
  useEffect(() => {
    // When the console is embedded during deployment, /console/ will exist.
    // This placeholder keeps Docusaurus builds passing even before the embed step.
    window.location.replace('/console/');
  }, []);

  return (
    <Layout title="Console" description="arifOS Metabolic Console">
      <main className="container margin-vert--lg">
        <h1>Console</h1>
        <p>Redirecting to the Metabolic Console...</p>
        <p>
          If nothing happens, open <a href="/console/">/console/</a>.
        </p>
      </main>
    </Layout>
  );
}

