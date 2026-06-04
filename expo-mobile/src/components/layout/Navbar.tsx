import { StyleSheet, Text, View } from 'react-native';
import { useTheme } from '@/hooks/useTheme';

export default function Navbar() {
  const { colors } = useTheme();
  return (
    <View style={[styles.nav, { backgroundColor: colors.card, borderBottomColor: colors.border }]}>
      <Text style={[styles.title, { color: colors.foreground }]}>Lumi</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  nav: {
    height: 56,
    borderBottomWidth: 1,
    justifyContent: 'center',
    paddingHorizontal: 16,
  },
  title: {
    fontSize: 18,
    fontWeight: '700',
  },
});
