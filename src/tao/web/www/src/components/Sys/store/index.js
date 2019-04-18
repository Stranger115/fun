'use strict'

import { observable, computed, extendObservable } from 'mobx'

class Store {

  @observable siteConfig = observable.map({})

}

export default new Store()
