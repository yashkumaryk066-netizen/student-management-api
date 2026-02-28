import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Alert, Image } from 'react-native';
import * as LocalAuthentication from 'expo-local-authentication';
import { ShieldCheck, Fingerprint, Lock } from 'lucide-react-native';

/**
 * Sovereign Pro: Advanced Biometric Security Layer
 * Implements Enterprise-grade Fingerprint/FaceID Authentication
 */
const BioAuthScreen = ({ onAuthSuccess }) => {
    const [isBiometricSupported, setIsBiometricSupported] = useState(false);

    useEffect(() => {
        (async () => {
            const compatible = await LocalAuthentication.hasHardwareAsync();
            setIsBiometricSupported(compatible);
        })();
    }, []);

    const handleAuthentication = async () => {
        try {
            const results = await LocalAuthentication.authenticateAsync({
                promptMessage: 'Login to Sovereign ERP',
                fallbackLabel: 'Enter Password',
                disableDeviceFallback: false,
            });

            if (results.success) {
                onAuthSuccess();
            } else {
                Alert.alert('Auth Failed', 'Identity verification failed. Please try again.');
            }
        } catch (error) {
            console.error(error);
        }
    };

    return (
        <View style={styles.container}>
            <View style={styles.glassCard}>
                <ShieldCheck color="#3b82f6" size={64} style={styles.icon} />
                <Text style={styles.title}>Secure Access</Text>
                <Text style={styles.subtitle}>Identity Verification Required</Text>

                <TouchableOpacity
                    style={styles.authButton}
                    onPress={handleAuthentication}
                >
                    <Fingerprint color="white" size={24} />
                    <Text style={styles.buttonText}>Authenticate</Text>
                </TouchableOpacity>

                <View style={styles.footer}>
                    <Lock color="#94a3b8" size={14} />
                    <Text style={styles.footerText}>Enterprise Encryption Active</Text>
                </div>
            </View>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#0f172a',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 20
    },
    glassCard: {
        width: '100%',
        maxWidth: 340,
        backgroundColor: 'rgba(30, 41, 59, 0.7)',
        borderRadius: 30,
        padding: 40,
        alignItems: 'center',
        borderWidth: 1,
        borderColor: 'rgba(59, 130, 246, 0.3)',
    },
    title: {
        color: 'white',
        fontSize: 24,
        fontWeight: 'bold',
        marginTop: 20,
    },
    subtitle: {
        color: '#94a3b8',
        fontSize: 16,
        marginTop: 10,
        marginBottom: 30,
    },
    authButton: {
        backgroundColor: '#3b82f6',
        flexDirection: 'row',
        alignItems: 'center',
        paddingVertical: 15,
        paddingHorizontal: 30,
        borderRadius: 15,
        gap: 10,
        shadowColor: "#3b82f6",
        shadowOffset: { width: 0, height: 10 },
        shadowOpacity: 0.3,
        shadowRadius: 20,
        elevation: 10
    },
    buttonText: {
        color: 'white',
        fontWeight: 'bold',
        fontSize: 16
    },
    footer: {
        flexDirection: 'row',
        alignItems: 'center',
        marginTop: 40,
        gap: 5
    },
    footerText: {
        color: '#64748b',
        fontSize: 12,
        fontWeight: '500'
    }
});

export default BioAuthScreen;
