import React from "react";
import {
  HomeIcon,
  TrendingUpIcon,
  VolumeIcon,
  BarChartIcon,
  HelpIcon,
  SettingsIcon,
} from "./Icons";

interface MobileNavProps {
  activeSection: string;
  onNavigate: (section: string) => void;
}

// A fixed bottom navigation bar that appears on < md screens
const MobileNav: React.FC<MobileNavProps> = ({ activeSection, onNavigate }) => {
  // An array to DRY-up the markup
  const navItems: { id: string; label: string; Icon: React.FC<{ size?: number }> }[] = [
    { id: "home", label: "Home", Icon: HomeIcon },
    { id: "trends", label: "Trends", Icon: TrendingUpIcon },
    { id: "voice", label: "Voice", Icon: VolumeIcon },
    { id: "analytics", label: "Analytics", Icon: BarChartIcon },
    { id: "help", label: "Help", Icon: HelpIcon },
    { id: "settings", label: "Settings", Icon: SettingsIcon },
  ];

  return (
    <nav
      className="fixed bottom-0 left-0 right-0 z-40 bg-[#e8eef5] backdrop-blur-sm border-t border-white/30 shadow-md md:hidden"
      style={{ paddingBottom: "calc(env(safe-area-inset-bottom, 0px) + 0.25rem)" }}
    >
      <ul className="flex justify-around py-2">
        {navItems.map(({ id, label, Icon }) => (
          <li key={id}>
            <button
              aria-label={label}
              title={label}
              onClick={() => onNavigate(id)}
              className={
                `flex flex-col items-center justify-center text-xs font-medium transition-all duration-200 min-w-[48px] ` +
                (activeSection === id
                  ? "text-blue-600 scale-110"
                  : "text-gray-600 hover:text-blue-500 hover:scale-105")
              }
            >
              <Icon size={22} />
              <span className="mt-1">{label}</span>
            </button>
          </li>
        ))}
      </ul>
    </nav>
  );
};

export default MobileNav; 