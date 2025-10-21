# VitePress Theme Customization

This theme extends the default VitePress theme with AfriGen-D branding and optimized logo styling.

## Logo Styling

The custom CSS optimizes the display of the AfriGen-D logo (512x178 wide format):

- **Navigation bar**: 28px height, auto width with aspect ratio preserved
- **Mobile**: 24px height for better mobile display
- **Dark mode**: Slight brightness adjustment for better visibility
- **Hero section**: Maximum 200px height on homepage
- **Sidebar**: 32px height

## Brand Colors

- **Primary Green**: `#2E7D32` - AfriGen-D primary brand color
- **Accent Orange**: `#FFA000` - Secondary accent color
- **Additional shades**: Light and dark variants for hover states

## Usage

The theme is automatically applied. To customize further:

1. Edit `style.css` for styling changes
2. Edit `index.ts` to add Vue components or plugins
3. Colors can be adjusted using CSS custom properties

## Template Variables

When using this template, no changes to the theme are needed. The logo path in config.ts should remain as `/logo.png`.