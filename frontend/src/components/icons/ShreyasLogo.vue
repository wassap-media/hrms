<template>
	<div class="flex items-center gap-3">
		<!-- Abstract Logo with three intertwined ribbon shapes -->
		<div class="relative w-8 h-8">
			<!-- Top ribbon (pink) -->
			<svg class="absolute inset-0 w-full h-full" viewBox="0 0 32 32" fill="none">
				<path
					d="M8 12 Q16 8 24 12 Q20 16 16 20 Q12 16 8 12 Z"
					fill="#FF69B4"
					opacity="0.9"
				/>
			</svg>
			<!-- Middle ribbon (green) -->
			<svg class="absolute inset-0 w-full h-full" viewBox="0 0 32 32" fill="none">
				<path
					d="M6 18 Q16 14 26 18 Q22 22 16 26 Q10 22 6 18 Z"
					fill="#32CD32"
					opacity="0.8"
				/>
			</svg>
			<!-- Bottom ribbon (blue) -->
			<svg class="absolute inset-0 w-full h-full" viewBox="0 0 32 32" fill="none">
				<path
					d="M4 24 Q16 20 28 24 Q24 28 16 32 Q8 28 4 24 Z"
					fill="#4169E1"
					opacity="0.7"
				/>
			</svg>
		</div>
		
		<!-- Text "Shreyas" -->
		<div class="flex flex-col">
			<span class="text-xl font-bold text-pink-500 italic">Shreyas</span>
			<div class="w-full h-0.5 bg-gray-300"></div>
		</div>
	</div>
</template>

<script setup>
// No props or logic needed for this logo component
</script>
