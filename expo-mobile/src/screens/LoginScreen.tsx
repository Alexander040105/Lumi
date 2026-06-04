import { useState } from 'react';
import {
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { useAuth } from '@/hooks/useAuth';
import { useTheme } from '@/hooks/useTheme';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Toast from 'react-native-toast-message';

type Mode = 'login' | 'signup' | 'reset';

export default function LoginScreen() {
  const { session, signInWithProvider, signInWithPassword, signUp, resetPassword } = useAuth();
  const { colors } = useTheme();
  const [mode, setMode] = useState<Mode>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [busy, setBusy] = useState(false);

  if (session) {
    return (
      <View style={[styles.center, { backgroundColor: colors.background }]}>
        <Text style={{ color: colors.foreground }}>Already signed in</Text>
      </View>
    );
  }

  const handleSubmit = async () => {
    if (!email) {
      Toast.show({ type: 'error', text1: 'Email is required' });
      return;
    }
    if (mode !== 'reset' && !password) {
      Toast.show({ type: 'error', text1: 'Password is required' });
      return;
    }
    setBusy(true);

    try {
      if (mode === 'signup' && password !== confirmPassword) {
        Toast.show({ type: 'error', text1: 'Passwords do not match' });
        setBusy(false);
        return;
      }

      if (mode === 'login') {
        const { error } = await signInWithPassword(email, password);
        if (error) throw error;
        Toast.show({ type: 'success', text1: 'Signed in successfully' });
      } else if (mode === 'signup') {
        const { error } = await signUp(email, password);
        if (error) throw error;
        Toast.show({
          type: 'success',
          text1: 'Check your email to confirm your account',
        });
      } else if (mode === 'reset') {
        const { error } = await resetPassword(email);
        if (error) throw error;
        Toast.show({ type: 'success', text1: 'Password reset email sent' });
      }
    } catch (error: any) {
      Toast.show({
        type: 'error',
        text1: error?.message || 'Authentication failed',
      });
    } finally {
      setBusy(false);
    }
  };

  return (
    <ScrollView
      style={[styles.container, { backgroundColor: colors.background }]}
      contentContainerStyle={styles.content}
    >
      <Card>
        <Text style={[styles.title, { color: colors.foreground }]}>
          Welcome back
        </Text>
        <Text style={[styles.desc, { color: colors.mutedForeground }]}>
          Use email/password or Google sign in.
        </Text>

        <View style={styles.tabs}>
          <Button
            title="Sign in"
            variant={mode === 'login' ? 'default' : 'outline'}
            onPress={() => setMode('login')}
          />
          <Button
            title="Sign up"
            variant={mode === 'signup' ? 'default' : 'outline'}
            onPress={() => setMode('signup')}
          />
        </View>

        <View style={styles.form}>
          <Input
            placeholder="Email"
            keyboardType="email-address"
            autoCapitalize="none"
            value={email}
            onChangeText={setEmail}
          />
          {mode !== 'reset' && (
            <Input
              placeholder="Password"
              secureTextEntry
              value={password}
              onChangeText={setPassword}
            />
          )}
          {mode === 'signup' && (
            <Input
              placeholder="Confirm password"
              secureTextEntry
              value={confirmPassword}
              onChangeText={setConfirmPassword}
            />
          )}
          <Button
            title={
              mode === 'login'
                ? 'Sign in'
                : mode === 'signup'
                  ? 'Create account'
                  : 'Send reset email'
            }
            onPress={handleSubmit}
            disabled={busy}
          />
        </View>

        {mode !== 'reset' ? (
          <Button
            title="Forgot password?"
            variant="ghost"
            onPress={() => setMode('reset')}
          />
        ) : (
          <Button
            title="Back to sign in"
            variant="ghost"
            onPress={() => setMode('login')}
          />
        )}

        <Button
          title="Continue with Google"
          variant="outline"
          onPress={() => signInWithProvider('google')}
        />
      </Card>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    padding: 16,
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    fontSize: 20,
    fontWeight: '700',
    marginBottom: 4,
  },
  desc: {
    fontSize: 13,
    marginBottom: 16,
  },
  tabs: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 16,
  },
  form: {
    gap: 10,
    marginBottom: 12,
  },
});
