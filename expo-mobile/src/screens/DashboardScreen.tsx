import { useEffect, useState } from 'react';
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
import Badge from '@/components/ui/Badge';
import Input from '@/components/ui/Input';
import LoadingSkeleton from '@/components/shared/LoadingSkeleton';
import { getHealth, getProtectedMe } from '@/services/apiClient';
import { supabase } from '@/services/supabaseClient';
import Toast from 'react-native-toast-message';

export default function DashboardScreen() {
  const { accessToken, user, signOut } = useAuth();
  const { colors } = useTheme();
  const emailVerified = Boolean(
    (user as any)?.email_confirmed_at || (user as any)?.confirmed_at
  );
  const [profile, setProfile] = useState<Record<string, unknown> | null>(null);
  const [health, setHealth] = useState<{ status: string; service: string } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [mfaStatus, setMfaStatus] = useState<{
    currentLevel: string | null;
    nextLevel: string | null;
  }>({ currentLevel: null, nextLevel: null });
  const [totpFactorId, setTotpFactorId] = useState('');
  const [totpQr, setTotpQr] = useState('');
  const [totpSecret, setTotpSecret] = useState('');
  const [mfaCode, setMfaCode] = useState('');
  const [mfaBusy, setMfaBusy] = useState(false);
  const [label, setLabel] = useState('');

  useEffect(() => {
    if (!accessToken) return;
    Promise.all([getProtectedMe(accessToken), getHealth()])
      .then(([me, healthStatus]) => {
        setProfile(me.user);
        setHealth(healthStatus);
      })
      .catch((err) => setError(err.message));
  }, [accessToken]);

  useEffect(() => {
    if (!accessToken) return;
    const loadMfa = async () => {
      const { data: assurance, error: assuranceError } =
        await supabase.auth.mfa.getAuthenticatorAssuranceLevel();
      if (!assuranceError && assurance) {
        setMfaStatus({
          currentLevel: assurance.currentLevel as string,
          nextLevel: assurance.nextLevel as string,
        });
      }
      const { data: factorsData } = await supabase.auth.mfa.listFactors();
      const totpFactor = (factorsData as any)?.totp?.[0];
      if (totpFactor?.id) {
        setTotpFactorId(totpFactor.id);
      }
    };
    loadMfa();
  }, [accessToken]);

  const handleEnrollTotp = async () => {
    setMfaBusy(true);
    try {
      const { data, error: enrollError } = await supabase.auth.mfa.enroll({
        factorType: 'totp',
      });
      if (enrollError) throw enrollError;
      setTotpFactorId(data.id);
      setTotpQr((data as any).totp.qr_code);
      setTotpSecret((data as any).totp.secret);
      Toast.show({
        type: 'success',
        text1: 'MFA enrolled. Scan the QR code and verify.',
      });
    } catch (error: any) {
      Toast.show({ type: 'error', text1: error?.message || 'MFA enrollment failed' });
    } finally {
      setMfaBusy(false);
    }
  };

  const handleVerifyTotp = async () => {
    if (!totpFactorId) {
      Toast.show({ type: 'error', text1: 'Enroll MFA first' });
      return;
    }
    setMfaBusy(true);
    try {
      const { data: challenge, error: challengeError } =
        await supabase.auth.mfa.challenge({ factorId: totpFactorId });
      if (challengeError) throw challengeError;
      const { error: verifyError } = await supabase.auth.mfa.verify({
        factorId: totpFactorId,
        challengeId: challenge.id,
        code: mfaCode,
      });
      if (verifyError) throw verifyError;
      Toast.show({ type: 'success', text1: 'MFA verified' });
      setMfaCode('');
    } catch (error: any) {
      Toast.show({ type: 'error', text1: error?.message || 'MFA verification failed' });
    } finally {
      setMfaBusy(false);
    }
  };

  return (
    <ScrollView
      style={[styles.container, { backgroundColor: colors.background }]}
      contentContainerStyle={styles.content}
    >
      <Text style={[styles.heading, { color: colors.foreground }]}>
        Dashboard
      </Text>
      <Text style={[styles.sub, { color: colors.mutedForeground }]}>
        Signed in as {(user as any)?.email || 'unknown'}
      </Text>

      <Button title="Sign out" variant="outline" onPress={() => signOut()} />

      {error && (
        <Card style={{ borderColor: colors.destructive }}>
          <Text style={{ color: colors.destructive }}>{error}</Text>
        </Card>
      )}

      {!emailVerified && (
        <Card style={{ borderColor: colors.warning }}>
          <Text style={[styles.cardTitle, { color: colors.warning }]}>
            Email not verified
          </Text>
          <Text style={{ color: colors.mutedForeground }}>
            Check your inbox and verify your email to unlock API access.
          </Text>
        </Card>
      )}

      {!profile && !error && <LoadingSkeleton />}

      {profile && (
        <>
          <Card>
            <Text style={[styles.cardTitle, { color: colors.foreground }]}>
              JWT Claims
            </Text>
            <Text style={[styles.pre, { color: colors.mutedForeground }]}>
              {JSON.stringify(profile, null, 2)}
            </Text>
          </Card>

          <Card>
            <Text style={[styles.cardTitle, { color: colors.foreground }]}>
              API Health
            </Text>
            <Badge
              title={health?.status || 'unknown'}
              variant={health?.status === 'ok' ? 'default' : 'secondary'}
            />
            <Text style={{ color: colors.mutedForeground, marginTop: 8 }}>
              Service: {health?.service || '-'}
            </Text>
          </Card>

          <Card>
            <Text style={[styles.cardTitle, { color: colors.foreground }]}>
              MFA (TOTP)
            </Text>
            <Text style={{ color: colors.mutedForeground }}>
              Current assurance: {mfaStatus.currentLevel || '-'}
            </Text>
            <Text style={{ color: colors.mutedForeground }}>
              Next assurance: {mfaStatus.nextLevel || '-'}
            </Text>
            {totpSecret && (
              <Text
                style={[
                  styles.pre,
                  { color: colors.mutedForeground, marginTop: 8 },
                ]}
              >
                Secret: {totpSecret}
              </Text>
            )}
            <View style={{ gap: 8, marginTop: 12 }}>
              <Button
                title="Enroll TOTP"
                variant="outline"
                onPress={handleEnrollTotp}
                disabled={mfaBusy}
              />
              <Input
                placeholder="Authenticator code"
                value={mfaCode}
                onChangeText={setMfaCode}
                keyboardType="number-pad"
              />
              <Button
                title="Verify code"
                onPress={handleVerifyTotp}
                disabled={mfaBusy || !mfaCode}
              />
            </View>
          </Card>

          <Card>
            <Text style={[styles.cardTitle, { color: colors.foreground }]}>
              Quick form
            </Text>
            <View style={{ gap: 8, marginTop: 8 }}>
              <Input
                placeholder="New label"
                value={label}
                onChangeText={setLabel}
              />
              <Button
                title="Save"
                onPress={() => {
                  Toast.show({ type: 'success', text1: `Saved: ${label}` });
                  setLabel('');
                }}
              />
            </View>
          </Card>

          <Card>
            <Text style={[styles.cardTitle, { color: colors.foreground }]}>
              Recent activity
            </Text>
            {['Auth', 'Billing', 'Analytics'].map((row) => (
              <View
                key={row}
                style={[
                  styles.tableRow,
                  { borderBottomColor: colors.border },
                ]}
              >
                <Text style={{ color: colors.foreground, flex: 1 }}>{row}</Text>
                <Badge title="In progress" variant="secondary" />
                <Text
                  style={{
                    color: colors.mutedForeground,
                    flex: 1,
                    textAlign: 'right',
                  }}
                >
                  Team Lumi
                </Text>
              </View>
            ))}
          </Card>
        </>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    padding: 16,
    gap: 12,
  },
  heading: {
    fontSize: 24,
    fontWeight: '700',
  },
  sub: {
    fontSize: 14,
    marginBottom: 8,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
  },
  pre: {
    fontSize: 11,
    fontFamily: 'monospace',
    marginTop: 8,
  },
  tableRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
  },
});
