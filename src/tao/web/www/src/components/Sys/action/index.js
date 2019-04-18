'use strict'

import { action } from 'mobx'
import store from '../store'

class Actions {
  constructor(store) {
    this.store = store
  }

  @action
  merge (target, src) {
    if (src) {
      target.merge(src)
    } else {
      Object.assign(this.store, target || {})
    }
  }

}

export default new Actions(store)
