import React, { useState } from 'react';
import { SafeAreaView, StatusBar, StyleSheet } from 'react-native';
import BioAuthScreen from './src/screens/BioAuthScreen';
import MainWebView from './src/components/MainWebView';

/**
 * Sovereign ERP Pro - Official Native Mobile Application
 * High-Performance Enterprise Edition
 */
export default function App() {
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    // REPLACE WITH YOUR PRODUCTION DOMAIN
    const ERP_PRODUCTION_URL = 'https://your-production-url.com';

    return (
        <SafeAreaView style={styles.container}>
            <StatusBar barStyle="light-content" backgroundColor="#0f172a" />

            {!isAuthenticated ? (
                <BioAuthScreen onAuthSuccess={() => setIsAuthenticated(true)} />
            ) : (
                <MainWebView url={`${ERP_PRODUCTION_URL}?mode=app_pro`} />
            )}

        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#0f172a',
    },
});
