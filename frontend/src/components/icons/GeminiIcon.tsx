export default function GeminiIcon({ className = "w-6 h-6" }: { className?: string }) {
  return (
    <svg 
      viewBox="0 0 24 24" 
      fill="none" 
      xmlns="http://www.w3.org/2000/svg" 
      className={className}
    >
      <path 
        d="M16.0077 1.00003C15.6599 5.37329 14.5029 8.2323 11.9999 11.9999C8.23242 14.5028 5.37329 15.6599 1.00003 16.0077C5.37329 16.3555 8.23242 17.5126 11.9999 20.0155C14.5029 23.7831 15.6599 26.6421 16.0077 31.0154C16.3555 26.6421 17.5126 23.7831 20.0155 20.0155C23.7831 17.5126 26.6421 16.3555 31.0154 16.0077C26.6421 15.6599 23.7831 14.5028 20.0155 11.9999C17.5126 8.2323 16.3555 5.37329 16.0077 1.00003Z" 
        transform="scale(0.75) translate(4, -4)" // Центруємо трохи
        fill="url(#gemini-gradient)" 
      />
      <defs>
        <linearGradient id="gemini-gradient" x1="0" y1="0" x2="32" y2="32" gradientUnits="userSpaceOnUse">
          <stop stopColor="#4E75F6" />
          <stop offset="1" stopColor="#E24869" />
        </linearGradient>
      </defs>
    </svg>
  );
}