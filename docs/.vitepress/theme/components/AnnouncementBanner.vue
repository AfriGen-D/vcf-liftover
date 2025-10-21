<template>
  <div v-if="!dismissed" class="announcement-banner">
    <div class="announcement-content">
      <div class="announcement-icon">
        🎉
      </div>
      <div class="announcement-text">
        <span class="announcement-title">{{ title }}</span>
        <span class="announcement-details">{{ details }}</span>
      </div>
      <a v-if="link" :href="link" class="announcement-link">
        Get Started →
      </a>
      <button @click="dismiss" class="announcement-close" aria-label="Close announcement">
        ×
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  title: String,
  details: String,
  link: String
})

const dismissed = ref(false)

onMounted(() => {
  // Check if user has already dismissed this announcement
  const dismissedKey = `announcement-dismissed-${props.title}`
  dismissed.value = localStorage.getItem(dismissedKey) === 'true'
})

const dismiss = () => {
  dismissed.value = true
  const dismissedKey = `announcement-dismissed-${props.title}`
  localStorage.setItem(dismissedKey, 'true')
}
</script>

<style scoped>
.announcement-banner {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  padding: 12px 0;
  position: sticky;
  top: 0;
  z-index: 999;
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
  animation: slideDown 0.5s ease-out;
}

.announcement-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 0 24px;
}

.announcement-icon {
  font-size: 1.5rem;
  animation: bounce 2s infinite;
}

.announcement-text {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.announcement-title {
  font-weight: 600;
  font-size: 1rem;
}

.announcement-details {
  font-size: 0.875rem;
  opacity: 0.9;
}

.announcement-link {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  padding: 8px 16px;
  border-radius: 6px;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.announcement-link:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.announcement-close {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.3s ease;
  opacity: 0.7;
}

.announcement-close:hover {
  opacity: 1;
  background: rgba(255, 255, 255, 0.1);
}

@keyframes slideDown {
  from {
    transform: translateY(-100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-4px);
  }
  60% {
    transform: translateY(-2px);
  }
}

@media (max-width: 768px) {
  .announcement-content {
    padding: 0 16px;
    gap: 12px;
  }
  
  .announcement-text {
    gap: 2px;
  }
  
  .announcement-title {
    font-size: 0.9rem;
  }
  
  .announcement-details {
    font-size: 0.8rem;
  }
  
  .announcement-link {
    padding: 6px 12px;
    font-size: 0.875rem;
  }
}
</style>
