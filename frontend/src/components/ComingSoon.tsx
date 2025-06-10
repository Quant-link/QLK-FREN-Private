import React from 'react';

interface ComingSoonProps {
  title: string;
}

const ComingSoon: React.FC<ComingSoonProps> = ({ title }) => {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center animate-fade-in p-8 select-none">
      <h2 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-[#4cafd8] to-[#3a9ec6] bg-clip-text text-transparent mb-4">
        {title}
      </h2>
      <p className="text-lg md:text-xl text-gray-600 max-w-md">
        This feature is currently under development and will be available soon. Stay tuned!
      </p>
    </div>
  );
};

export default ComingSoon; 