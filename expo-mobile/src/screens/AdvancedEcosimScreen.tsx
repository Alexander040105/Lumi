import { useState } from 'react';
import {
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  View,
} from 'react-native';
import { useTheme } from '@/hooks/useTheme';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import LoadingSkeleton from '@/components/shared/LoadingSkeleton';
import { postEcosim } from '@/services/apiClient';
import Toast from 'react-native-toast-message';
import type { EcosimResponse } from '@/types';

export default function AdvancedEcosimScreen() {
  const { colors } = useTheme();
  const [houseName, setHouseName] = useState('');
  const [municipality, setMunicipality] = useState('');
  const [currentBill, setCurrentBill] = useState('');
  const [electricityRate, setElectricityRate] = useState('14.35');
  const [desiredSavings, setDesiredSavings] = useState('0.50');
  const [includeAi, setIncludeAi] = useState(true);
  const [useRag, setUseRag] = useState(true);
  const [ragQuery, setRagQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<EcosimResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    setError(null);
    setLoading(true);
    try {
      const data = await postEcosim(
        {
          house_name: houseName,
          municipality,
          current_electricity_bill: parseFloat(currentBill),
          electricity_rate: parseFloat(electricityRate),
          desired_savings: parseFloat(desiredSavings),
        },
        includeAi,
        useRag,
        ragQuery || undefined
      );
      setResult(data);
      Toast.show({ type: 'success', text1: 'Simulation complete' });
    } catch (err: any) {
      setError(err?.message || 'Unable to run advanced simulation.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView
      style={[styles.container, { backgroundColor: colors.background }]}
      contentContainerStyle={styles.content}
    >
      <Text style={[styles.heading, { color: colors.foreground }]}>
        Advanced Ecosim
      </Text>
      <Text style={[styles.sub, { color: colors.mutedForeground }]}>
        AI-powered renewable energy analysis with RAG context.
      </Text>

      <Card>
        <Text style={[styles.cardTitle, { color: colors.foreground }]}>
          House Details
        </Text>
        <View style={styles.form}>
          <Input
            placeholder="House name"
            value={houseName}
            onChangeText={setHouseName}
          />
          <Input
            placeholder="Municipality"
            value={municipality}
            onChangeText={setMunicipality}
          />
          <Input
            placeholder="Current electricity bill (PHP)"
            keyboardType="numeric"
            value={currentBill}
            onChangeText={setCurrentBill}
          />
          <Input
            placeholder="Electricity rate (PHP/kWh)"
            keyboardType="numeric"
            value={electricityRate}
            onChangeText={setElectricityRate}
          />
          <Input
            placeholder="Desired savings (0.0 - 1.0)"
            keyboardType="numeric"
            value={desiredSavings}
            onChangeText={setDesiredSavings}
          />
        </View>
      </Card>

      <Card>
        <Text style={[styles.cardTitle, { color: colors.foreground }]}>
          AI Options
        </Text>
        <View style={styles.switchRow}>
          <Text style={{ color: colors.foreground }}>Include AI analysis</Text>
          <Switch
            value={includeAi}
            onValueChange={setIncludeAi}
            thumbColor={includeAi ? colors.primary : colors.muted}
          />
        </View>
        <View style={styles.switchRow}>
          <Text style={{ color: colors.foreground }}>Use RAG</Text>
          <Switch
            value={useRag}
            onValueChange={setUseRag}
            thumbColor={useRag ? colors.primary : colors.muted}
          />
        </View>
        <Input
          placeholder="RAG query (optional)"
          value={ragQuery}
          onChangeText={setRagQuery}
        />
        <Button
          title={loading ? 'Running...' : 'Run advanced simulation'}
          onPress={handleSubmit}
          disabled={loading || !houseName || !municipality || !currentBill}
        />
      </Card>

      {error && (
        <Card style={{ borderColor: colors.destructive }}>
          <Text style={{ color: colors.destructive }}>{error}</Text>
        </Card>
      )}

      {loading && <LoadingSkeleton />}

      {result && !loading && (
        <>
          <Card>
            <Text style={[styles.cardTitle, { color: colors.foreground }]}>
              Consumption
            </Text>
            <Text style={{ color: colors.mutedForeground }}>
              Monthly: {result.consumption_results.monthly_consumption_kwh} kWh
            </Text>
            <Text style={{ color: colors.mutedForeground }}>
              Daily: {result.consumption_results.daily_consumption_kwh} kWh
            </Text>
            <Text style={{ color: colors.mutedForeground }}>
              Target: {result.consumption_results.target_monthly_consumption_kwh} kWh
            </Text>
          </Card>

          {result.ai_analysis && (
            <Card>
              <Text style={[styles.cardTitle, { color: colors.foreground }]}>
                AI Analysis
              </Text>
              <Text style={[styles.pre, { color: colors.mutedForeground }]}>
                {JSON.stringify(result.ai_analysis, null, 2)}
              </Text>
            </Card>
          )}
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
    fontSize: 22,
    fontWeight: '700',
  },
  sub: {
    fontSize: 14,
    lineHeight: 20,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
  },
  form: {
    gap: 10,
  },
  switchRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  pre: {
    fontSize: 11,
    fontFamily: 'monospace',
    marginTop: 8,
  },
});
