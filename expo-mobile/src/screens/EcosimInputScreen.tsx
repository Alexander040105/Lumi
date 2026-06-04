import { useEffect, useState } from 'react';
import {
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { Picker } from '@react-native-picker/picker';
import { useTheme } from '@/hooks/useTheme';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import LoadingSkeleton from '@/components/shared/LoadingSkeleton';
import { getEcosim, getMunicipalities } from '@/services/apiClient';
import Toast from 'react-native-toast-message';
import type { MunicipalityOption, EcosimDashboardResponse } from '@/types';

export default function EcosimInputScreen() {
  const navigation = useNavigation<any>();
  const { colors } = useTheme();
  const [municipalityId, setMunicipalityId] = useState('');
  const [municipalities, setMunicipalities] = useState<MunicipalityOption[]>([]);
  const [municipalitiesError, setMunicipalitiesError] = useState<string | null>(null);
  const [monthlyConsumption, setMonthlyConsumption] = useState('350');
  const [monthlyBill, setMonthlyBill] = useState('5000');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isActive = true;
    const loadMunicipalities = async () => {
      try {
        const data = await getMunicipalities();
        if (!isActive) return;
        const items = data?.items || [];
        setMunicipalities(items);
        if (items.length) {
          setMunicipalityId(String(items[0].municipality_id));
        }
      } catch (err: any) {
        if (!isActive) return;
        setMunicipalitiesError(err?.message || 'Unable to load municipalities.');
      }
    };
    loadMunicipalities();
    return () => {
      isActive = false;
    };
  }, []);

  const handleSubmit = async () => {
    setError(null);
    setLoading(true);
    try {
      const data = await getEcosim({
        municipalityId: String(municipalityId).trim(),
        monthlyConsumption: String(monthlyConsumption).trim(),
        monthlyBill: String(monthlyBill).trim(),
      });
      navigation.getParent()?.navigate('EcosimResults', { result: data });
    } catch (err: any) {
      setError(err?.message || 'Unable to load Ecosim data.');
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
        Renewable Energy Simulation
      </Text>
      <Text style={[styles.sub, { color: colors.mutedForeground }]}>
        Ecosim evaluates solar, wind, and hydropower options for your location
        based on consumption patterns and environmental data.
      </Text>

      <Card>
        <Text style={[styles.cardTitle, { color: colors.foreground }]}>
          Simulation Inputs
        </Text>
        <Text style={[styles.cardDesc, { color: colors.mutedForeground }]}>
          Provide your current usage and location to generate a recommendation.
        </Text>

        <View style={styles.form}>
          <View style={styles.field}>
            <Text style={[styles.label, { color: colors.foreground }]}>
              Monthly consumption (kWh)
            </Text>
            <Input
              keyboardType="numeric"
              value={monthlyConsumption}
              onChangeText={setMonthlyConsumption}
            />
          </View>

          <View style={styles.field}>
            <Text style={[styles.label, { color: colors.foreground }]}>
              Monthly bill (PHP)
            </Text>
            <Input
              keyboardType="numeric"
              value={monthlyBill}
              onChangeText={setMonthlyBill}
            />
          </View>

          <View style={styles.field}>
            <Text style={[styles.label, { color: colors.foreground }]}>
              Municipality
            </Text>
            <View
              style={[
                styles.pickerWrap,
                {
                  borderColor: colors.input,
                  backgroundColor: colors.background,
                },
              ]}
            >
              <Picker
                selectedValue={municipalityId}
                onValueChange={(itemValue: string) => setMunicipalityId(itemValue)}
                style={{ color: colors.foreground }}
                dropdownIconColor={colors.foreground}
              >
                {municipalities.map((item) => (
                  <Picker.Item
                    key={item.municipality_id}
                    label={item.name}
                    value={String(item.municipality_id)}
                  />
                ))}
              </Picker>
            </View>
            {municipalitiesError && (
              <Text style={{ color: colors.destructive, fontSize: 12 }}>
                {municipalitiesError}
              </Text>
            )}
          </View>

          <Button
            title={loading ? 'Running simulation...' : 'Run simulation'}
            onPress={handleSubmit}
            disabled={loading || !municipalityId}
          />
        </View>
      </Card>

      {error && (
        <Card style={{ borderColor: colors.destructive }}>
          <Text style={[styles.cardTitle, { color: colors.destructive }]}>
            Simulation error
          </Text>
          <Text style={{ color: colors.mutedForeground }}>{error}</Text>
        </Card>
      )}

      {loading && <LoadingSkeleton />}
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
    marginBottom: 4,
  },
  cardDesc: {
    fontSize: 13,
    marginBottom: 12,
  },
  form: {
    gap: 12,
  },
  field: {
    gap: 4,
  },
  label: {
    fontSize: 13,
    fontWeight: '500',
  },
  pickerWrap: {
    borderWidth: 1,
    borderRadius: 6,
    overflow: 'hidden',
  },
});
