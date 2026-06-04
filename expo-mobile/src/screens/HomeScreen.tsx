import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useTheme } from '@/hooks/useTheme';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';

export default function HomeScreen() {
  const { colors } = useTheme();
  const navigation = useNavigation<any>();

  return (
    <ScrollView
      style={[styles.container, { backgroundColor: colors.background }]}
      contentContainerStyle={styles.content}
    >
      <View style={styles.header}>
        <Badge title="React Native + Expo" variant="secondary" />
        <Text style={[styles.heading, { color: colors.foreground }]}>
          Build your next full-stack product faster.
        </Text>
        <Text style={[styles.subtext, { color: colors.mutedForeground }]}>
          A clean UI foundation with Supabase auth, FastAPI integration, and a
          scalable component system ready for dashboards and SaaS workflows.
        </Text>
        <View style={styles.row}>
          <Button
            title="Open dashboard"
            onPress={() => navigation.navigate('Dashboard')}
          />
          <Button
            title="Go to login"
            variant="outline"
            onPress={() => navigation.navigate('Login')}
          />
        </View>
      </View>

      <View style={styles.grid}>
        {['Auth ready', 'Design system', 'API connected', 'Dark mode'].map(
          (title) => (
            <Card key={title}>
              <Text style={[styles.cardTitle, { color: colors.foreground }]}>
                {title}
              </Text>
              <Text
                style={[styles.cardDesc, { color: colors.mutedForeground }]}
              >
                Production-ready defaults and clean structure.
              </Text>
            </Card>
          )
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    padding: 16,
    gap: 16,
  },
  header: {
    gap: 10,
  },
  heading: {
    fontSize: 24,
    fontWeight: '700',
  },
  subtext: {
    fontSize: 14,
    lineHeight: 20,
  },
  row: {
    flexDirection: 'row',
    gap: 10,
    marginTop: 4,
  },
  grid: {
    gap: 10,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 4,
  },
  cardDesc: {
    fontSize: 13,
  },
});
