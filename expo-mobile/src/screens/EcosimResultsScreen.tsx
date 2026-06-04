import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { useRoute } from '@react-navigation/native';
import { useTheme } from '@/hooks/useTheme';
import Card from '@/components/ui/Card';
import { EcosimDashboardResponse } from '@/types';

const formatNumber = (value: number | undefined, digits = 0) =>
  new Intl.NumberFormat('en-US', { maximumFractionDigits: digits }).format(
    value ?? 0
  );

const formatCurrency = (value: number | undefined) =>
  new Intl.NumberFormat('en-PH', {
    style: 'currency',
    currency: 'PHP',
    maximumFractionDigits: 0,
  }).format(value ?? 0);

export default function EcosimResultsScreen() {
  const route = useRoute<any>();
  const { colors } = useTheme();
  const result: EcosimDashboardResponse | undefined = route.params?.result;

  if (!result) {
    return (
      <View style={[styles.center, { backgroundColor: colors.background }]}>
        <Text style={{ color: colors.mutedForeground }}>No results</Text>
      </View>
    );
  }

  const comparisonMax = Math.max(
    ...result.options.map((item) => item.estimated_generation_kwh || 0),
    1
  );

  return (
    <ScrollView
      style={[styles.container, { backgroundColor: colors.background }]}
      contentContainerStyle={styles.content}
    >
      <Text style={[styles.heading, { color: colors.foreground }]}>
        Simulation Results
      </Text>

      <Card>
        <Text style={[styles.cardTitle, { color: colors.foreground }]}>
          Recommendation
        </Text>
        <Text style={[styles.cardDesc, { color: colors.mutedForeground }]}>
          Best-fit renewable source for {result.municipality}
        </Text>
        <View style={styles.grid3}>
          <View>
            <Text style={{ color: colors.mutedForeground, fontSize: 12 }}>
              Recommended source
            </Text>
            <Text style={[styles.value, { color: colors.foreground }]}>
              {result.recommended_source}
            </Text>
          </View>
          <View>
            <Text style={{ color: colors.mutedForeground, fontSize: 12 }}>
              Suitability score
            </Text>
            <Text style={[styles.value, { color: colors.foreground }]}>
              {formatNumber(result.suitability_score, 2)}
            </Text>
          </View>
          <View>
            <Text style={{ color: colors.mutedForeground, fontSize: 12 }}>
              Estimated generation
            </Text>
            <Text style={[styles.value, { color: colors.foreground }]}>
              {formatNumber(result.estimated_generation_kwh)} kWh/mo
            </Text>
          </View>
        </View>
        <View
          style={[
            styles.explanation,
            { backgroundColor: colors.muted + '40', borderColor: colors.border },
          ]}
        >
          <Text style={{ color: colors.mutedForeground, fontSize: 13 }}>
            {result.explanation}
          </Text>
        </View>
      </Card>

      <View style={styles.metricsRow}>
        {[
          {
            label: 'Estimated monthly generation',
            value: `${formatNumber(result.estimated_generation_kwh)} kWh`,
          },
          {
            label: 'Estimated savings',
            value: formatCurrency(result.monthly_savings),
          },
          {
            label: 'Installation cost',
            value: formatCurrency(result.installation_cost),
          },
          {
            label: 'Payback period',
            value: result.payback_years
              ? `${formatNumber(result.payback_years, 1)} yrs`
              : 'N/A',
          },
          {
            label: 'Carbon reduction',
            value: `${formatNumber(result.carbon_reduction)} kg CO2/mo`,
          },
        ].map((metric) => (
          <Card key={metric.label} style={{ flex: 1, minWidth: 140 }}>
            <Text style={{ color: colors.mutedForeground, fontSize: 11 }}>
              {metric.label}
            </Text>
            <Text
              style={[styles.metricValue, { color: colors.foreground }]}
            >
              {metric.value}
            </Text>
          </Card>
        ))}
      </View>

      <Card>
        <Text style={[styles.cardTitle, { color: colors.foreground }]}>
          Renewable comparison
        </Text>
        <Text style={[styles.cardDesc, { color: colors.mutedForeground }]}>
          Monthly generation and savings across options.
        </Text>
        {result.options.map((option) => (
          <View key={option.source} style={{ marginBottom: 12 }}>
            <View style={styles.barHeader}>
              <Text style={{ color: colors.foreground, fontWeight: '500' }}>
                {option.source}
              </Text>
              <Text style={{ color: colors.mutedForeground }}>
                {formatNumber(option.estimated_generation_kwh)} kWh/mo
              </Text>
            </View>
            <View
              style={[
                styles.barTrack,
                { backgroundColor: colors.muted },
              ]}
            >
              <View
                style={[
                  styles.barFill,
                  {
                    backgroundColor: colors.primary,
                    width: `${
                      (option.estimated_generation_kwh / comparisonMax) * 100
                    }%`,
                  },
                ]}
              />
            </View>
            <Text style={{ color: colors.mutedForeground, fontSize: 11 }}>
              {option.explanation}
            </Text>
          </View>
        ))}
      </Card>

      <Card>
        <Text style={[styles.cardTitle, { color: colors.foreground }]}>
          Scenario comparison
        </Text>
        <Text style={[styles.cardDesc, { color: colors.mutedForeground }]}>
          Current usage vs recommended renewable offset.
        </Text>
        {[
          {
            scenario: 'Current',
            consumption: formatNumber(result.comparison.current_monthly_consumption_kwh),
            bill: formatCurrency(result.comparison.current_monthly_bill),
          },
          {
            scenario: `With ${result.recommended_source}`,
            consumption: formatNumber(
              result.comparison.renewable_monthly_consumption_kwh
            ),
            bill: formatCurrency(result.comparison.renewable_monthly_bill),
          },
        ].map((row) => (
          <View
            key={row.scenario}
            style={[
              styles.tableRow,
              { borderBottomColor: colors.border },
            ]}
          >
            <Text style={{ color: colors.foreground, flex: 1 }}>
              {row.scenario}
            </Text>
            <Text
              style={{ color: colors.mutedForeground, flex: 1, textAlign: 'right' }}
            >
              {row.consumption} kWh
            </Text>
            <Text
              style={{ color: colors.mutedForeground, flex: 1, textAlign: 'right' }}
            >
              {row.bill}
            </Text>
          </View>
        ))}
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
    gap: 12,
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  heading: {
    fontSize: 22,
    fontWeight: '700',
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 4,
  },
  cardDesc: {
    fontSize: 13,
    marginBottom: 12,
    color: '#71717a',
  },
  grid3: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    marginBottom: 12,
  },
  value: {
    fontSize: 20,
    fontWeight: '700',
    marginTop: 2,
  },
  explanation: {
    borderRadius: 6,
    borderWidth: 1,
    padding: 12,
  },
  metricsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  metricValue: {
    fontSize: 18,
    fontWeight: '700',
    marginTop: 4,
  },
  barHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  barTrack: {
    height: 8,
    borderRadius: 4,
    overflow: 'hidden',
    marginBottom: 4,
  },
  barFill: {
    height: 8,
    borderRadius: 4,
  },
  tableRow: {
    flexDirection: 'row',
    paddingVertical: 8,
    borderBottomWidth: 1,
  },
});
