<template>
  <div>
    <p>VueSesion holder</p>
    <p>{{ user }}</p>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  data () {
    return {
      user: null
    }
  },
  methods: {
    getUserFromBackend () {
      const path = `http://localhost:5000/whoami`
      axios.get(path)
        .then(response => {
          this.user = response.data.user
        })
        .catch(error => {
          console.log(error)
        })
    }

  },
  created () {
    this.getUserFromBackend()
  }
}
</script>

<style>

</style>
