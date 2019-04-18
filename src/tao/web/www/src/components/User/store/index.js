'use strict'

import { observable, computed, extendObservable } from 'mobx'

class Store {

  @observable user = observable.map({})
}

export default new Store()
