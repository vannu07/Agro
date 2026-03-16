import type { GetServerSideProps } from 'next';
import Head from 'next/head';
import React, { useEffect, useState } from 'react';

interface PageProps {
  title: string;
  html: string;
}

export default function Home({ html }: PageProps) {
  const [flaskReady, setFlaskReady] = useState(false);

  useEffect(() => {
    // Check if Flask is running
    fetch('/api/health')
      .then(() => setFlaskReady(true))
      .catch(() => setFlaskReady(false));
  }, []);

  if (!flaskReady) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <h1>Krishi Mitr - Loading...</h1>
        <p>Make sure the Flask app is running on port 5000</p>
        <p>Run: <code>cd app && python app.py</code></p>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>Krishi Mitr - AI-Powered Smart Farming Assistant</title>
        <meta name="description" content="AI-powered agricultural assistance for Indian farmers" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="theme-color" content="#10B981" />
      </Head>
      <iframe
        src="http://localhost:5000/"
        style={{
          width: '100%',
          height: '100vh',
          border: 'none',
          margin: 0,
          padding: 0,
        }}
        title="Krishi Mitr"
      />
    </>
  );
}

export const getServerSideProps: GetServerSideProps<PageProps> = async (context) => {
  // In production, this will be replaced with actual Next.js pages
  return {
    props: {
      title: 'Krishi Mitr - Home',
      html: '<h1>Welcome to Krishi Mitr</h1>',
    },
  };
};
