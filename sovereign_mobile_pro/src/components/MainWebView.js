import React, { useRef, useState } from 'react';
import { StyleSheet, View, ActivityIndicator, BackHandler } from 'react-native';
import { WebView } from 'react-native-webview';

/**
 * Sovereign Pro: High-Performance Enterprise WebView
 * Optimized for complex data tables and live dashboard rendering
 */
const MainWebView = ({ url }) => {
    const webViewRef = useRef(null);
    const [loading, setLoading] = useState(true);

    // Deep Research: Handling Native Back Button for Web Navigation
    React.useEffect(() => {
        const backAction = () => {
            if (webViewRef.current) {
                webViewRef.current.goBack();
                return true;
            }
            return false;
        };
        const backHandler = BackHandler.addEventListener('hardwareBackPress', backAction);
        return () => backHandler.remove();
    }, []);

    // Secure Session Injection Script
    const INJECTED_JAVASCRIPT = `
        (function() {
            window.isNativeApp = true;
            document.body.classList.add('mobile-native-shell');
            // Notify web app about native environment
            window.postMessage('NATIVE_BRIDGE_READY');
        })();
    `;

    return (
        <View style={styles.container}>
            <WebView
                ref={webViewRef}
                source={{ uri: url }}
                style={styles.webview}
                onLoadStart={() => setLoading(true)}
                onLoadEnd={() => setLoading(false)}
                injectedJavaScript={INJECTED_JAVASCRIPT}
                javaScriptEnabled={true}
                domStorageEnabled={true}
                allowsBackForwardNavigationGestures={true}
                pullToRefreshEnabled={true}
                onMessage={(event) => {
                    console.log('Mobile Bridge Message:', event.nativeEvent.data);
                }}
            />
            {loading && (
                <View style={styles.loadingOverlay}>
                    <ActivityIndicator size="large" color="#3b82f6" />
                </View>
            )}
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#0f172a',
    },
    webview: {
        flex: 1,
        backgroundColor: '#0f172a',
    },
    loadingOverlay: {
        ...StyleSheet.absoluteFillObject,
        backgroundColor: '#0f172a',
        justifyContent: 'center',
        alignItems: 'center',
    }
});

export default MainWebView;
