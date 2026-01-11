/**
 * VastuWise AI - Theme Configuration
 * Central export for all theme values
 */

export { colors } from './colors';
export { typography } from './typography';
export { spacing, borderRadius } from './spacing';

// Combined theme object
export const theme = {
  colors: require('./colors').colors,
  typography: require('./typography').typography,
  spacing: require('./spacing').spacing,
  borderRadius: require('./spacing').borderRadius,
};

export default theme;
